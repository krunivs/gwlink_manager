# Create your views here.
from gwlink_manager.common.error import get_exception_traceback, GSLinkManagerError
from gwlink_manager.settings import get_logger
from utils.http_utils import HttpResponse
from utils.validate import Validator

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from cluster import views as cluster_views
from workloads import views as workloads_views
from service import views as service_views
from django.http import HttpResponse as http_response

logger = get_logger(__name__)

""" Kubernetes manifest APIs """
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
            context = method(argv[0], argv[1], argv[2], argv[3])
        elif len(argv) == 5:
            context = method(argv[0], argv[1], argv[2], argv[3], argv[4])
        else:
            logger.error('number of argument exceeds 4')

        return HttpResponse.http_return_200_ok(context)

    except ValueError as exc:
        if len(exc.args) > 0:
            error_message = ' '.join(exc.args)
        return HttpResponse.http_return_400_bad_request(error_message)
    except KeyError as exc:
        if len(exc.args) > 0:
            error_message = ' '.join(exc.args)
        return HttpResponse.http_return_400_bad_request(error_message)
    except ConnectionError as exc:
        if len(exc.args) > 0:
            error_message = ' '.join(exc.args)
        return HttpResponse.http_return_500_internal_server_error(error_message)

    except SystemError as exc:
        if len(exc.args) > 0:
            error_message = ' '.join(exc.args)
        return HttpResponse.http_return_500_internal_server_error(error_message)

    except Exception as exc:
        error_message = get_exception_traceback(exc)
        return HttpResponse.http_return_500_internal_server_error(error_message)


def get_timeout_options(request) -> (bool, int):
    """
    get await option from query params
    :param request: (rest_framework.request.Request)
    :return:
    (bool) True - has timeout option, False - no timeout option
    (int) timeout;
    timeout < 0: blocking,
    timeout = 0: asynchronous
    timeout > 0: await seconds
    """
    timeout = -1
    ok = False

    if 'timeout' in request.query_params:
        val = request.query_params['timeout']
        if 's' in val:
            val = val.replace('s', '')

        if not Validator.is_enable_cast_to_int(val):
            err = 'Invalid value for timeout. Must input integer as seconds'
            raise ValueError(err)

        timeout = int(val)
        ok = True

    return ok, timeout


""" Cluster management APIs """

@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def manage_clusters(request):
    """
    manage clusters
    (IFD0001_CLS_001) retrieve cluster list
    - GET /api/app/v1/clusters
    (IFD0001_CLS_001.01) retrieve cluster list filtered by cluster name
    - GET /api/app/v1/clusters?name=:cluster_name
    (IFD001_CLS_003) register cluster
    - POST /api/app/v1/clusters
    :param request: (rest_framework.request.Request)
    :return:
    """
    # IFD0001_CLS_001, IFD0001_CLS_001.01
    if request.method == 'GET':
        return rest_api_handler(
            cluster_views.get_cluster_list_view, request.query_params)

    # IFD001_CLS_003
    if request.method == 'POST':
        return rest_api_handler(
            cluster_views.register_cluster, request.data)


@api_view(['GET', 'DELETE', ])
@permission_classes((AllowAny,))
def manage_cluster(request, cluster):
    """
    manage single cluster
    (IFD001_CLS_002) retrieve specified cluster
    - GET /api/app/v1/clusters/:cluster
    (IFD001_CLS_004) delete specified cluster
    - DELETE /api/app/v1/clusters/:cluster?timeout=<int:seconds>
      timeout > 0: await seconds
      timeout = 0: no wait
      timeout < 0: max timeout(3600s)
      no timeout query param: default timeout(60s)
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :return:
    """
    # IFD001_CLS_002
    if request.method == 'GET':
        return rest_api_handler(
            cluster_views.get_cluster_view, cluster)

    # IFD001_CLS_004
    if request.method == 'DELETE':
        # cleanup cedge-agent(trigger exit and delete cedge-agent resource)
        # delete cluster entry from database(TODO)
        try:
            has_timeout, timeout = get_timeout_options(request)
        except ValueError:
            return HttpResponse.http_return_400_bad_request(
                'Invalid timeout value. Must input integer as seconds')

        if has_timeout:
            return rest_api_handler(
                cluster_views.delete_cluster, cluster, timeout)
        else:
            return rest_api_handler(
                cluster_views.delete_cluster, cluster)


@api_view(['GET', ])
@permission_classes((AllowAny,))
def get_cluster_components_conditions(request, cluster):
    """
    (IFD001_CLS_002.1) get conditions for cluster's primary components
    - GET /api/app/v1/clusters/:cluster/conditions
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :return:
    """
    # IFD001_CLS_002.1
    if request.method == 'GET':
        return rest_api_handler(
            cluster_views.get_cluster_component_condition_list_view, cluster)


@api_view(['POST', ])
@permission_classes((AllowAny,))
def connect_mc_network(request, cluster):
    """
    (IFD001_CLS_005) connect multicluster network
    - POST /api/app/v1/clusters/:cluster/mc/connect?timeout=<int:seconds>
      timeout > 0: await seconds
      timeout = 0: no wait
      timeout < 0: max timeout(3600s)
      no timeout query param: default timeout(60s)
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :return:
    """
    try:
        has_timeout, timeout = get_timeout_options(request)
    except ValueError:
        return HttpResponse.http_return_400_bad_request(
            'Invalid timeout value. Must input integer as seconds')

    if has_timeout:
        return rest_api_handler(
            cluster_views.connect_mc_network, cluster, request.data, timeout)

    return rest_api_handler(
        cluster_views.connect_mc_network, cluster, request.data)


@api_view(['POST', ])
@permission_classes((AllowAny,))
def disconnect_mc_network(request, cluster):
    """
    (IFD001_CLS_006) disconnect multicluster network throughput
    - POST /api/app/v1/clusters/:cluster/mc/disconnect?timeout=<int:seconds>
      timeout > 0: await seconds
      timeout = 0: no wait
      timeout < 0: max timeout(3600s)
      no timeout: default timeout(60s)
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :return:
    """
    try:
        has_timeout, timeout = get_timeout_options(request)
    except ValueError:
        return HttpResponse.http_return_400_bad_request(
            'Invalid timeout value. Must input integer as seconds')

    # IFD001_CLS_006
    if has_timeout:
        return rest_api_handler(
            cluster_views.disconnect_mc_network, cluster, timeout)

    return rest_api_handler(
        cluster_views.disconnect_mc_network, cluster)


@api_view(['GET', ])
@permission_classes((AllowAny,))
def get_mc_network_metrics(request, cluster, endpoint):
    """
    (IFD001_CLS_008) retrieve multicluster network metrics(rx_bytes, tx_bytes, latencies)
    - GET /api/app/v1/clusters/:cluster/mc/metrics
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :param endpoint: (str) connected cluster name
    :return:
    """
    return rest_api_handler(
        cluster_views.get_mc_network_metric_view, cluster, endpoint)


""" Node management APIs """
@api_view(['GET', ])
@permission_classes((AllowAny,))
def get_nodes(request, cluster):
    """
    (IFD001_NODE_001) retrieve node list
    - GET /api/app/v1/clusters/:cluster/nodes
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :return:
    """
    return rest_api_handler(
        cluster_views.get_nodes_view, cluster)


@api_view(['GET', ])
@permission_classes((AllowAny,))
def get_node(request, cluster, node):
    """
    (IFD001_NODE_002) retrieve specified node
    - GET /api/app/v1/clusters/:cluster/nodes/:node
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :param node: (str) node name
    :return:
    """
    return rest_api_handler(
        cluster_views.get_nodes_view, cluster, node)


@api_view(['GET', ])
@permission_classes((AllowAny,))
def get_node_metrics(request, cluster, node):
    """
    (IFD001_NODE_003) retrieve specified node metrics
    - GET /api/app/v1/clusters/:cluster/nodes/:node/metrics
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :param node: (str) node name
    :return:
    """
    return rest_api_handler(
        cluster_views.get_node_metrics_view, cluster, node)


""" Kubernetes resource management APIs """
""" Namespace management APIs """
@api_view(['GET', ])
@permission_classes((AllowAny,))
def get_namespace_list(request, cluster):
    """
    (IFD001_NS_001) retrieve kubernetes namespace list
    - GET /api/app/v1/clusters/:cluster/namespaces
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :return:
    """
    if cluster == '_all_':
        return rest_api_handler(
            workloads_views.get_all_namespace_list)

    return rest_api_handler(
        workloads_views.get_namespace_list_view, cluster)

@api_view(['DELETE', ])
@permission_classes((AllowAny,))
def manage_namespace(request, cluster, namespace):
    """
    (IFD001_NS_002) delete kubernetes namespace
    - DELETE /api/app/v1/clusters/:cluster/namespaces/:namespace
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :param namespace: (str) namespace name
    :return:
    """
    # IFD001_NS_002
    if request.method == 'DELETE':
        try:
            has_timeout, timeout = get_timeout_options(request)
        except ValueError:
            return HttpResponse.http_return_400_bad_request(
                'Invalid timeout value. Must input integer as seconds')

        if has_timeout:
            return rest_api_handler(
                workloads_views.delete_namespace, cluster, namespace, timeout)

        return rest_api_handler(
            workloads_views.delete_namespace, cluster, namespace)


""" Pod management APIs """
@api_view(['GET', ])
@permission_classes((AllowAny,))
def get_pod_list(request, cluster, namespace):
    """
    (IFD001_POD_001) retrieve kubernetes pod list
    - GET /api/app/v1/clusters/:cluster/namespaces/:namespace/pods
    (IFD001_POD_002) retrieve kubernetes pod list filtered by service or deployment, daemonset
    - GET /api/app/v1/clusters/:cluster/namespaces/:namespace/pods?service=:service
    - GET /api/app/v1/clusters/:cluster/namespaces/:namespace/pods?deployment=:deployment
    - GET /api/app/v1/clusters/:cluster/namespaces/:namespace/pods?daemonset=:daemonset
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :param namespace: (str) namespace name
    :return:
    """
    return rest_api_handler(
        workloads_views.get_pod_list_view, cluster, namespace, request.query_params)


@api_view(['GET', 'DELETE'])
@permission_classes((AllowAny,))
def manage_pod(request, cluster, namespace, pod):
    """
    (IFD001_POD_003) retrieve kubernetes specified pod
    - GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/pods/<str:pod>
    (IFD001_POD_004) delete kubernetes specified pod
    - DELETE /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/pods/<str:pod>?timeout=<int:seconds>
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :param namespace: (str) namespace name
    :param pod: (str) pod name
    :return:
    """
    # IFD001_POD_003
    if request.method == 'GET':
        return rest_api_handler(
            workloads_views.get_pod_view, cluster, namespace, pod)

    # IFD001_POD_004
    elif request.method == 'DELETE':
        try:
            has_timeout, timeout = get_timeout_options(request)
        except ValueError:
            return HttpResponse.http_return_400_bad_request(
                'Invalid timeout value. Must input integer as seconds')

        if has_timeout:
            return rest_api_handler(
                workloads_views.delete_pod, cluster, namespace, pod, timeout)

        return rest_api_handler(
            workloads_views.delete_pod, cluster, namespace, pod)


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def manage_pod_migration(request, cluster, namespace, pod):
    """
    (IFD001_POD_005) retrieve kubernetes pod migration hint
    - GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/pods/<str:pod>/migrate
    (IFD001_POD_006) run kubernetes pod migration
    - POST /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/pods/<str:pod>/migrate
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :param namespace: (str) namespace name
    :param pod: (str) pod name
    :return:
    """
    # IFD001_POD_005
    if request.method == 'GET':
        return rest_api_handler(
            workloads_views.get_pod_migratable_cluster_list_view, cluster, namespace, pod)

    # IFD001_POD_006
    if request.method == 'POST':
        return rest_api_handler(
            workloads_views.do_pod_migration, request, cluster, namespace, pod)

@api_view(['GET', ])
@permission_classes((AllowAny,))
def manage_pod_migration_log_list(request, cluster):
    """
    (IFD001_POD_007) retrieve pod migration log list
    - GET /api/app/v1/clusters/<str:cluster>/migration_logs
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :return:
    """
    # IFD001_POD_007
    if request.method == 'GET':
        return rest_api_handler(
                workloads_views.get_pod_migration_log_list_view, cluster)


@api_view(['GET', 'DELETE' ])
@permission_classes((AllowAny,))
def manage_pod_migration_log(request, cluster, migration_id):
    """
    (IFD001_POD_008) delete pod migration log
    - DELETE /api/app/v1/clusters/<str:cluster>/migration_logs/<str:migration_id>
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :param migration_id: (str) migration UUID
    :return:
    """
    # IFD001_POD_008
    if request.method == 'DELETE':
        return rest_api_handler(
            workloads_views.delete_pod_migration_log, cluster, migration_id)


""" Deployment management APIs """
@api_view(['GET', ])
@permission_classes((AllowAny,))
def get_deployment_list(request, cluster, namespace):
    """
    (IFD001_DEPLOY_001) retrieve kubernetes deployment list
    - GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/deployments
    (IFD001_DEPLOY_002) retrieve kubernetes deployment list filtered by pod
    - GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/deployments?pod=<str:pod>
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :param namespace: (str) namespace name
    :return:
    """
    return rest_api_handler(
        workloads_views.get_deployment_list_view, cluster, namespace, request.query_params)


@api_view(['GET', 'DELETE'])
@permission_classes((AllowAny,))
def manage_deployment(request, cluster, namespace, deployment):
    """
    (IFD001_DEPLOY_003) retrieve kubernetes specified deployment
    - GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/deployments/<str:deployment>
    (IFD001_DEPLOY_004) delete kubernetes specified deployment
    - DELETE /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/deployments/<str:deployment>?timeout=<int:seconds>
      timeout > 0: await seconds
      timeout = 0: no wait
      timeout < 0: max timeout(3600s)
      no timeout query param: default timeout(60s)
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :param namespace: (str) namespace name
    :param deployment: (str) deployment name
    :return:
    """
    # IFD001_DEPLOY_003
    if request.method == 'GET':
        return rest_api_handler(
            workloads_views.get_deployment_view, cluster, namespace, deployment)

    # IFD001_DEPLOY_004
    elif request.method == 'DELETE':
        try:
            has_timeout, timeout = get_timeout_options(request)
        except ValueError:
            return HttpResponse.http_return_400_bad_request(
                'Invalid timeout value. Must input integer as seconds')
        if has_timeout:
            return rest_api_handler(
                workloads_views.delete_deployment, cluster, namespace, deployment, timeout)

        return rest_api_handler(
            workloads_views.delete_deployment, cluster, namespace, deployment)


""" DaemonSet management APIs """
@api_view(['GET', ])
@permission_classes((AllowAny,))
def get_daemonset_list(request, cluster, namespace):
    """
    (IFD001_DAEMON_001) retrieve kubernetes daemonset list
    - GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/daemonsets
    (IFD001_DAEMON_002) retrieve kubernetes daemonset list filtered by pod
    - GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/daemonsets?pod=<str:pod>
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :param namespace: (str) namespace name
    :return:
    """
    return rest_api_handler(
        workloads_views.get_daemonset_list_view, cluster, namespace, request.query_params)


@api_view(['GET', 'DELETE'])
@permission_classes((AllowAny,))
def manage_daemonset(request, cluster, namespace, daemonset):
    """
    (IFD001_DAEMON_003) retrieve kubernetes specified daemonset
    - GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/daemonsets/<str:daemonset>
    (IFD001_DAEMON_004) delete kubernetes specified daemonset
    - DELETE /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/daemonsets/<str:daemonset>?timeout=<int:seconds>
      timeout > 0: await seconds
      timeout = 0: no wait
      timeout < 0: max timeout(3600s)
      no timeout query param: default timeout(60s)
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :param namespace: (str) namespace name
    :param daemonset: (str) daemonset name
    :return:
    """
    if request.method == 'GET':
        return rest_api_handler(
            workloads_views.get_daemonset_view, cluster, namespace, daemonset)

    elif request.method == 'DELETE':
        try:
            has_timeout, timeout = get_timeout_options(request)
        except ValueError:
            return HttpResponse.http_return_400_bad_request(
                'Invalid timeout value. Must input integer as seconds')
        if has_timeout:
            return rest_api_handler(
                workloads_views.delete_daemonset, cluster, namespace, daemonset, timeout)

        return rest_api_handler(
            workloads_views.delete_daemonset, cluster, namespace, daemonset)


""" Service management APIs """
@api_view(['GET', ])
@permission_classes((AllowAny,))
def get_service_list(request, cluster, namespace):
    """
    (IFD001_SERVICE_001) retrieve kubernetes service list
    - GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/services
    (IFD001_SERVICE_002) retrieve kubernetes service list filtered by pod
    - GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/services?pod=<str:pod>
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :param namespace: (str) namespace name
    :return:
    """
    if request.method == 'GET':
        return rest_api_handler(
            service_views.get_service_list_view, cluster, namespace, request.query_params)


@api_view(['GET', 'DELETE', ])
@permission_classes((AllowAny,))
def manage_service(request, cluster, namespace, service):
    """
    (IFD001_SERVICE_003) retrieve kubernetes specified service
    - GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/services/<str:service>
    (IFD001_SERVICE_004) delete kubernetes specified service
    - DELETE /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/services/<str:service>?timeout=<int:seconds>
      timeout > 0: await seconds
      timeout = 0: no wait
      timeout < 0: max timeout(3600s)
      no timeout query param: default timeout(60s)
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :param namespace: (str) namespace name
    :param service:
    :return:
    """
    # IFD001_SERVICE_003
    if request.method == 'GET':
        return rest_api_handler(
            service_views.get_service_view, cluster, namespace, service)

    # IFD001_SERVICE_004
    elif request.method == 'DELETE':
        try:
            has_timeout, timeout = get_timeout_options(request)
        except ValueError:
            return HttpResponse.http_return_400_bad_request(
                'Invalid timeout value. Must input integer as seconds')

        if has_timeout:
            return rest_api_handler(
                service_views.delete_service, cluster, namespace, service, timeout)

        return rest_api_handler(
            service_views.delete_service, cluster, namespace, service)


@api_view(['POST', ])
@permission_classes((AllowAny,))
def export_service(request, cluster, namespace, service):
    """
    (IFD001_SERVICE_005) export service to connected cluster
    - POST /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/services/<str:service>/export?timeout=<int:seconds>
      timeout > 0: await seconds
      timeout = 0: no wait
      timeout < 0: max timeout(3600s)
      no timeout query param: default timeout(60s)
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :param namespace: (str) namespace name
    :param service:
    :return:
    """
    try:
        has_timeout, timeout = get_timeout_options(request)
    except ValueError:
        return HttpResponse.http_return_400_bad_request(
            'Invalid timeout value. Must input integer as seconds')

    if has_timeout:
        return rest_api_handler(
            service_views.do_export_service, cluster, namespace, service, timeout)

    return rest_api_handler(
        service_views.do_export_service, cluster, namespace, service)


@api_view(['POST', ])
@permission_classes((AllowAny,))
def unexport_service(request, cluster, namespace, service):
    """
    (IFD001_SERVICE_006) unexport service from connected cluster
    - POST /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/services/<str:service>/unexport?timeout=<int:seconds>
      timeout > 0: await seconds
      timeout = 0: no wait
      timeout < 0: max timeout(3600s)
      no timeout query param: default timeout(60s)
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :param namespace: (str) namespace name
    :param service:
    :return:
    """
    try:
        has_timeout, timeout = get_timeout_options(request)
    except ValueError:
        return HttpResponse.http_return_400_bad_request(
            'Invalid timeout value. Must input integer as seconds')

    if has_timeout:
        return rest_api_handler(
            service_views.do_unexport_service, cluster, namespace, service, timeout)

    return rest_api_handler(
        service_views.do_unexport_service, cluster, namespace, service)


@api_view(['POST'])
@permission_classes((AllowAny,))
def apply_manifest(request, cluster):
    """
    (IFD001_MANIFEST_001) apply resource manifest file
    POST /api/app/v1/clusters/<str:cluster>/manifest/apply
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :return:
    """
    try:
        has_timeout, timeout = get_timeout_options(request)
    except ValueError:
        return HttpResponse.http_return_400_bad_request(
            'Invalid timeout value. Must input integer as seconds')

    if has_timeout:
        return rest_api_handler(
            cluster_views.apply_manifest, cluster, request.data, timeout)

    return rest_api_handler(
        cluster_views.apply_manifest, cluster, request.data)


@api_view(['POST'])
@permission_classes((AllowAny,))
def delete_manifest(request, cluster):
    """
    (IFD001_MANIFEST_002) delete resource manifest file
    POST /api/app/v1/clusters/<str:cluster>/manifest/delete
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :return:
    """
    try:
        has_timeout, timeout = get_timeout_options(request)
    except ValueError:
        return HttpResponse.http_return_400_bad_request(
            'Invalid timeout value. Must input integer as seconds')

    if has_timeout:
        return rest_api_handler(
            cluster_views.delete_manifest, cluster, request.data, timeout)

    return rest_api_handler(
        cluster_views.delete_manifest, cluster, request.data)


@api_view(['POST'])
@permission_classes((AllowAny,))
def validate_manifest(request, cluster):
    """
    (IFD001_MANIFEST_003) validate resource manifest file
    POST /api/app/v1/clusters/<str:cluster>/manifest/validate
    :param request: (rest_framework.request.Request)
    :param cluster: (str) cluster name
    :return:
    """
    try:
        has_timeout, timeout = get_timeout_options(request)
    except ValueError:
        return HttpResponse.http_return_400_bad_request(
            'Invalid timeout value. Must input integer as seconds')

    if has_timeout:
        return rest_api_handler(
            cluster_views.validate_manifest, cluster, request.data, timeout)

    return rest_api_handler(
        cluster_views.validate_manifest, cluster, request.data)

@api_view(['GET'])
@permission_classes((AllowAny,))
def get_gw_agent(request, cluster):
    """
    get gw-agent
    """
    try:
        agent_view = cluster_views.get_gw_agent(cluster)
    except ValueError as exc:
        return http_response(content="Bad Request(400)\n", content_type="text/plain", status=400)

    return http_response(content=agent_view, content_type="text/plain", status=200)