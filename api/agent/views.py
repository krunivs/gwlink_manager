from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# Create your views here.
from api.agent.event import EventDispatcher
from cache.request_cache import RequestCache
from gwlink_manager.common.error import get_exception_traceback
from gwlink_manager.settings import get_logger
from cluster import views as cluster_views
from cluster.data_access_object import ClusterDAO
from cluster.models import Cluster
from repository.cache.cluster import ClusterCache
from repository.common.type import ClusterSessionStatus, MultiClusterRole, SubmarinerState
from repository.model.k8s.resource import ResourceBulk
from utils.dateformat import DateFormatter
from utils.http_utils import HttpResponse


logger = get_logger(__name__)

def rest_api_handler(method, *argv):
    """
    rest_api_handler
    :param method: <class function>
    :param argv: arguments
    :return:
    """
    error_message = None

    try:
        context = None

        if len(argv) == 0:
            context = method()
        elif len(argv) == 1:
            context = method(argv[0])
        elif len(argv) == 2:
            context = method(argv[0], argv[1])
        elif len(argv) == 3:
            context = method(argv[0], argv[1], argv[2])
        elif len(argv) == 4:
            context = method(argv[0], argv[1], argv[3], argv[4])
        elif len(argv) == 5:
            context = method(argv[0], argv[1], argv[3], argv[4], argv[5])
        else:
            logger.error('number of argument exceeds 4')

        return HttpResponse.http_return_200_ok(context)

    except (ValueError, KeyError) as exc:
        if len(exc.args) > 0:
            error_message = ' '.join(exc.args)
        return HttpResponse.http_return_400_bad_request(error_message)

    except SystemError as exc:
        if len(exc.args) > 0:
            error_message = ' '.join(exc.args)
        return HttpResponse.http_return_500_internal_server_error(error_message)

    except Exception as exc:
        error_message = get_exception_traceback(exc)
        return HttpResponse.http_return_500_internal_server_error(error_message)

# todo:
#   modify @permission_classes((AllowAny,)) to @permission_classes((IsAuthenticated,))
#   and add token publish logics, rest api request logics with published token
def validate_response_body(body):
    """
    validate response body
    :param body: (dict) body from http response
    :return:
    (bool) ok; True - success, False - failure
    (rest_framework.response.Response)
    """
    if 'success' not in body:
        return False, HttpResponse.http_return_400_bad_request('Not found body param \'success\'')

    if 'error' not in body:
        return False, HttpResponse.http_return_400_bad_request('Not found body param \'error\'')

    if 'content' not in body:
        return False, HttpResponse.http_return_400_bad_request('Not found body param \'content\'')

    return True, None


@api_view(['POST'])
@permission_classes((AllowAny,))
def keep_alive(request, cluster):
    """
    keep alive from agent
    GET /api/agent/v1/cluster/:cluster/keep_alive
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :return:
    """
    keep_alive_view = {
        'cluster_session_status': ClusterSessionStatus.CLUSTER_SESSION_ESTABLISHED.value,
        'has_disconnect_request': False
    }

    # get body param
    body = request.data

    # error in body param
    if 'submariner_state' not in body:
        error = 'Key error in body. Not found \'resource\' in body.'
        logger.error(error)
        raise ValueError(error)

    # check whether cluster cache is created or not
    cache = ClusterCache().get_cluster(cluster)

    if not cache:
        keep_alive_view['cluster_session_status'] = ClusterSessionStatus.CLUSTER_SESSION_NOT_ESTABLISHED.value
        return HttpResponse.http_return_200_ok(keep_alive_view)

    ok, cluster_objects, error_message = ClusterDAO.get_cluster_objects_by_name(cluster_name=cluster)

    # cluster database error
    if not ok:
        logger.error('Failed in ClusterDAO.get_cluster_objects_by_name(cluster_name=cluster), '
                     'caused by ' + error_message)

        return HttpResponse.http_return_500_internal_server_error(error_message)

    # cluster not found error
    if not cluster_objects or len(cluster_objects) <= 0:
        return HttpResponse.http_return_400_bad_request('Not found cluster, cluster=' + cluster)

    # cluster not found error
    if not cluster_objects or len(cluster_objects) <= 0:
        return HttpResponse.http_return_400_bad_request('Not found cluster, cluster=' + cluster)

    # submariner status for cluster
    submariner_state = body['submariner_state']
    cache['submariner_state'] = submariner_state

    mc_config_state = cluster_objects[0].get('mc_config_state', None)

    if submariner_state in (SubmarinerState.BROKER_JOINED.value,
                            SubmarinerState.GATEWAY_CONNECTED.value,
                            SubmarinerState.GATEWAY_CONNECTING.value,
                            SubmarinerState.GATEWAY_CONNECT_ERROR.value):
        # update multi-cluster-config-state to connected
        if mc_config_state:
            if mc_config_state == Cluster.MultiClusterConfigState.CONNECTING.value:
                # If "connect" request is exist,
                ok, error_message = ClusterDAO.update_multi_cluster_config_state(
                    cluster_name=cluster_objects[0]['cluster_name'],
                    mc_config_state=Cluster.MultiClusterConfigState.CONNECTED.value)

                # database error
                if not ok:
                    logger.error(error_message)

            # If "disconnect" request is exist,
            if mc_config_state == Cluster.MultiClusterConfigState.DISCONNECT_PENDING.value:
                keep_alive_view['has_disconnect_request'] = True

                # update multi-cluster-config-state to disconnecting
                ok, error_message = ClusterDAO.update_multi_cluster_config_state(
                    cluster_name=cluster_objects[0]['cluster_name'],
                    mc_config_state=Cluster.MultiClusterConfigState.DISCONNECTING.value)

                # database error
                if not ok:
                    logger.error(error_message)

    if submariner_state == SubmarinerState.BROKER_READY.value:
        if mc_config_state == Cluster.MultiClusterConfigState.DISCONNECTING.value:
            # submariner broker cleaned status
            # reset multi-cluster-config-state when disconnected complete
            ok, error_message = ClusterDAO.update_multi_cluster_connection(
                cluster_name=cluster_objects[0]['cluster_name'],
                mc_connect_id=None,
                role=MultiClusterRole.NONE.value,
                mc_config_state=Cluster.MultiClusterConfigState.NONE.value,
                broker_info=None)

            if not ok:
                logger.error(error_message)

    cache['lastStateProbeTime'] = DateFormatter.current_datetime()

    return HttpResponse.http_return_200_ok(keep_alive_view)


@api_view(['POST'])
@permission_classes((AllowAny,))
def initialize_cluster(request, cluster):
    """
    register cluster session
    POST /api/agent/v1/cluster/:cluster/initialize
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :return:
    """
    # todo: authorize cluster from database

    # check http parameters
    if 'resource' not in request.data:
        return HttpResponse.http_return_400_bad_request('Key error in body. Not found \'resource\' in body.')

    resource_dict = request.data['resource']

    try:
        # dispatch cluster session initialize data
        resource_bulk = ResourceBulk.to_object(resource_dict)

    except Exception as exc:
        stderr = get_exception_traceback(exc)
        return HttpResponse.http_return_400_bad_request(stderr)

    # check whether cluster is already register or not
    cache = ClusterCache().get_cluster(cluster)

    # if cluster is already exist, clear session data
    if cache:
        cache.clear()

    # add cluster data to cache(cluster session)
    ClusterCache().add_cluster(cluster)

    try:
        # initialize cluster cache with resource_bulk
        ClusterCache().initialize_cluster(cluster, resource_bulk)
    except Exception as exc:
        stderr = get_exception_traceback(exc)
        return HttpResponse.http_return_500_internal_server_error(stderr)

    logger.debug('initialize cluster[{}] session.'.format(cluster))

    return HttpResponse.http_return_200_ok(None)


@api_view(['PUT'])
@permission_classes((AllowAny,))
def push_event(request, cluster):
    """
    push event
    PUT /api/agent/v1/cluster/:cluster/event
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :return:
    """
    try:
        EventDispatcher.dispatch(cluster, request.data)

    except Exception as exc:
        stderr = get_exception_traceback(exc)
        if type(exc) == KeyError:
            # it can occur when session initialize again after agent is restarted or recovered from failure
            logger.debug(stderr)
            return HttpResponse.http_return_400_bad_request(stderr)

        if type(exc) == ValueError:
            logger.debug(stderr)
            return HttpResponse.http_return_400_bad_request(stderr)

        else:
            logger.debug(stderr)
            return HttpResponse.http_return_500_internal_server_error(stderr)

    # logger.debug('cluster[{}] push event.'.format(cluster))

    return HttpResponse.http_return_200_ok(None)


@api_view(['PUT'])
@permission_classes((AllowAny,))
def push_response(request, cluster, request_id):
    """
    push response for request_id
    PUT /api/agent/v1/cluster/:cluster/request/:request_id
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :param request_id: (str) request id
    :return:
    """
    body = request.data

    ok, result = validate_response_body(body)
    if not ok:
        return result

    try:
        RequestCache().set_response(request_id,
                                    body['success'],
                                    body['error'],
                                    body['content']['result'])

    except Exception as exc:
        stderr = get_exception_traceback(exc)

        return HttpResponse.http_return_400_bad_request(stderr)

    return HttpResponse.http_return_200_ok(None)


@api_view(['GET'])
@permission_classes((AllowAny,))
def diagnose_multi_cluster_network(request, cluster):
    """
    get diagnosis for multi-cluster network
    GET /api/agent/v1/cluster/:cluster_id/diagnosis
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :return:
    """
    return rest_api_handler(
        cluster_views.diagnose_multi_cluster_network_failure, cluster)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_join_broker_info(request, mc_connect_id):
    """
    get local broker for cluster
    GET /api/agent/v1/cluster/mcn/:mc_connect_id/join-broker
    :param request:
    :param mc_connect_id: (str) multi-cluster connection id
    :return:
    """
    return rest_api_handler(
        cluster_views.get_join_broker_info, mc_connect_id)

#
# @api_view(['PUT'])
# @permission_classes((AllowAny,))
# def update_broker(request, cluster):
#     """
#     update multicluster broker_info-info.subm
#     PUT /api/agent/v1/cluster/:cluster/mcn/broker/update
#     :param request: (rest_framework.request.Request)
#     :param cluster: (str)
#     :return:
#     """
#     # validate 'broker_info' content in request body
#     if 'broker_info' not in request.data:
#         error = 'Key error in body. Not found \'broker_info\' in body.'
#         logger.error(error)
#         return HttpResponse.http_return_400_bad_request(error)
#
#     broker_info_content = request.data['broker_info']
#
#     if not broker_info_content or len(broker_info_content) <= 0:
#         error = 'Invalid \'broker_info\' value in body.'
#         logger.error(error)
#         return HttpResponse.http_return_400_bad_request(error)
#
#     # validate cluster name
#     ok, error, cluster_objects = \
#         ClusterDAO.get_cluster_objects_by_name(cluster_name=cluster)
#
#     if not ok:
#         error = 'Not found cluster. cluster_id={}'.format(cluster)
#         logger.error(error)
#         return HttpResponse.http_return_500_internal_server_error(error)
#
#     if not cluster_objects or len(cluster_objects) <= 0:
#         error = 'Not found cluster. cluster_id={}'.format(cluster)
#         logger.error(error)
#         return HttpResponse.http_return_500_internal_server_error(error)
#
#     # update local cluster's broker-info
#     ok, error, _ = ClusterDAO.update_cluster_broker_info(cluster_name=cluster,
#                                                                broker_info=broker_info_content)
#     if not ok:
#         logger.error(error)
#         return HttpResponse.http_return_500_internal_server_error(error)
#
#     # If connected_id is exist, requested cluster is one of multi-cluster.
#     connect_id = cluster_objects[0]['mc_connect_id']
#
#     if not connect_id:
#         return HttpResponse.http_return_200_ok({
#             'success': ok,
#             'result': '',
#             'error': error
#         })
#
#     ok, error, cluster_objects = \
#         ClusterDAO.get_cluster_objects_by_connected_id(connect_id)
#
#     if not ok or len(cluster_objects) <= 0:
#         error = 'Invalid connected_id. cluster_id={}'.format(cluster)
#         logger.error(error)
#         return HttpResponse.http_return_500_internal_server_error(error)
#
#     # connected cluster name with broker update request cluster
#     connected_cluster_name = None
#
#     for cluster_object in cluster_objects:
#         if cluster_object['cluster_name'] != cluster:
#             connected_cluster_name = cluster_object['cluster_name']
#
#     # if broker is updated, connected broker must be updated
#     request_id = None
#
#     if connected_cluster_name:
#         request_id = ClusterAgent.update_remote_broker(connected_cluster_name, broker_info_content)
#
#     if not request_id:
#         error = 'Fail to run ClusterAgent.update_remote_broker. ' \
#                 'connected_cluster_name={}'.format(connected_cluster_name)
#         logger.error(error)
#         return HttpResponse.http_return_500_internal_server_error(error)
#
#     # wait until agent's response arrive(timeout: 60s)
#     ok, stdout, stderr = RequestCache().wait(request_id, 60)
#
#     if not ok:
#         if stderr == RequestCache.NOT_READY or stderr == RequestCache.REQUEST_NOT_CACHED:
#             logger.error(stderr)
#             return HttpResponse.http_return_500_internal_server_error(stderr)
#
#     return HttpResponse.http_return_200_ok({
#         'success': ok,
#         'result': stdout,
#         'error': stderr
#     })

#
# @api_view(['PUT'])
# @permission_classes((AllowAny,))
# def get_broker_info_checksum(request, cluster):
#     """
#     GET /api/agent/v1/cluster/:cluster/mcn/broker
#     :param request: (rest_framework.request.Request)
#     :param cluster: (str) cluster name
#     :return:
#     """
#     # validate cluster name
#     ok, error, cluster_objects = \
#         ClusterDAO.get_cluster_objects_by_name(cluster_name=cluster)
#
#     if not ok:
#         error = 'Not found cluster. cluster_id={}'.format(cluster)
#         logger.error(error)
#         return HttpResponse.http_return_500_internal_server_error(error)
#
#     if not cluster_objects or len(cluster_objects) <= 0:
#         error = 'Not found cluster. cluster_id={}'.format(cluster)
#         logger.error(error)
#         return HttpResponse.http_return_500_internal_server_error(error)
#
#     broker_info_checksum = cluster_objects[0].get('broker_info_checksum', None)
#     broker_info_update_date = cluster_objects[0].get('broker_info_update_date', None)
#
#     return HttpResponse.http_return_200_ok({
#         'success': ok,
#         'result': {
#             'broker_info_checksum': broker_info_checksum,
#             'broker_info_update_date': broker_info_update_date
#         },
#         'error': error
#     })
