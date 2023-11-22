# Cluster Controllers
import os
from typing import List

import uuid

from cache.localhost import Configure
from cache.request_cache import RequestCache
from gwlink_manager import settings
from gwlink_manager.common.error import GSLinkManagerError
from cluster.data_access_object import ClusterDAO
from cluster.models import Cluster
from cluster.view_model import *
from mqtt.api import ClusterAgent
from repository.cache.cluster import ClusterCache
from repository.common.type import ClusterStatus, MultiClusterRole, MultiClusterNetworkDiagnosis, SubmarinerState, \
    MultiClusterNetworkStatus
from repository.model.k8s.node import Node
from utils.dateformat import DateFormatter
from utils.fileutils import FileUtil
from utils.validate import Validator

logger = settings.get_logger(__name__)

def get_cluster_name_list_view() -> dict:
    """
    get cluster name list
    :return: (dict) cluster.view_model.cluster_name_list_view_model
    """
    cluster_name_list_view = ClusterViewModel.get_cluster_name_list_view_model()
    ok, items, error_message  = ClusterDAO.get_all_cluster_id_and_name()

    if not ok:
        logger.error('Failed in ClusterDAO.get_all_cluster_id_and_name(), caused by ' + error_message)
        return cluster_name_list_view

    if len(items) != 0:
        for item in items:
            cluster_name = item.get('cluster_name', None)
            cluster_id = item.get('cluster_id', None)
            cache = ClusterCache().get_cluster(cluster_name)

            if cache and cache['state'] == ClusterStatus.ACTIVE.value:
                cluster_name_view = ClusterViewModel.get_cluster_name_view_model()
                cluster_name_view['id'] = cluster_id
                cluster_name_view['name'] = cluster_name
                cluster_name_list_view['clusters'].append(cluster_name_view)

    return cluster_name_list_view


def get_cluster_views(items: List[dict]) -> list:
    """
    get cluster context
    :param items: list[cluster.model.Cluster]
    :return: list[cluster.view_model.cluster_view_model]
    """
    cluster_views = []

    if not items:
        return cluster_views

    # fills cluster context
    for item in items:
        cluster_view = ClusterViewModel.get_cluster_view_model()
        mc_connect_id = item.get('mc_connect_id', None)
        mc_config_status = item.get('mc_config_state', None)
        cluster_name = item.get('cluster_name', None)
        cluster_view['id'] = item.get('cluster_id', None)
        cluster_view['name'] = cluster_name
        cluster_view['desc'] = item.get('description', None)
        registration = settings.CLUSTER_AGENT_DEPLOY_COMMAND.format(
            my_host=Configure().get_host(), my_port=Configure().get_http_port(), cluster=cluster_name)
        cluster_view['registration'] = registration
        cluster_view['mc_network']['connect_id'] = mc_connect_id
        cluster_view['mc_network']['status'] = ClusterStatus.UNAVAILABLE.value

        if mc_config_status == Cluster.MultiClusterConfigState.NONE.value or mc_config_status is None:
            mc_config_status = ClusterStatus.UNAVAILABLE.value

        # cluster info
        cache = ClusterCache().get_cluster(cluster_view['name'])

        if cache:
            submariner_state = cache['submariner_state']

            # redefine multi-cluster state with referring submariner state
            if submariner_state == SubmarinerState.BROKER_READY.value:  # Standby
                mc_config_status = MultiClusterNetworkStatus.STANDBY.value
            elif submariner_state in (SubmarinerState.BROKER_JOINED.value,
                                      SubmarinerState.BROKER_JOINING.value):
                mc_config_status = MultiClusterNetworkStatus.CONNECTING.value
            elif submariner_state == SubmarinerState.GATEWAY_CONNECTED.value: # Connected
                mc_config_status = MultiClusterNetworkStatus.CONNECTED.value
            elif submariner_state == SubmarinerState.GATEWAY_CONNECT_ERROR.value:   # Error
                mc_config_status = MultiClusterNetworkStatus.ERROR.value
            elif submariner_state == SubmarinerState.BROKER_CLEANING.value: # Disconnecting
                mc_config_status = MultiClusterNetworkStatus.DISCONNECTING.value
            elif submariner_state in (SubmarinerState.BROKER_DEPLOYING.value,
                                      SubmarinerState.BROKER_CLEANING.value,
                                      SubmarinerState.BROKER_NA.value):
                pass
            else:
                mc_config_status = MultiClusterNetworkStatus.UNAVAILABLE.value

            cluster_view['mc_network']['status'] = mc_config_status
            cluster_view['state'] = cache['state']
            resource = cache['resource']
            network = cache['network']
            component = cache['component']

            cluster_view['nodes'] = resource.get_number_of_nodes()
            if cluster_view['nodes'] > 0:
                master_node = resource.get_master_node()
                ip_address = master_node.get_ip()
                k8s_version_abb = None
                if resource.get_k8s_version():
                    k8s_version_abb = resource.get_k8s_version().split('-')[0]

                cluster_view['api_version'] = k8s_version_abb
                cluster_view['api_address'] = '{}:6443'.format(ip_address)

            # multi-cluster info
            if mc_connect_id:
                cluster_view['mc_network']['connect_id'] = mc_connect_id

                mc_network = network.get_mc_network()
                if mc_network:
                    cluster_view['mc_network']['globalnet'] = mc_network.get_globalnet()
                    cluster_view['mc_network']['global_cidr'] = mc_network.get_global_cidr()
                    cluster_view['mc_network']['cable_driver'] = mc_network.get_cable_driver()
                    cluster_view['mc_network']['broker_role'] = mc_network.get_broker_role()
                    local_endpoint = mc_network.get_local_endpoints()
                    remote_endpoint = mc_network.get_remote_endpoints()

                    if len(local_endpoint) > 0:
                        # multi-cluster local cluster info
                        cluster_view['mc_network']['local']['name'] = local_endpoint[0].get_name()
                        cluster_view['mc_network']['local']['public'] = local_endpoint[0].get_public_ip()
                        cluster_view['mc_network']['local']['gateway'] = local_endpoint[0].get_gateway_ip()
                        cluster_view['mc_network']['local']['service_cidr'] = local_endpoint[0].get_service_cidr()
                        cluster_view['mc_network']['local']['cluster_cidr'] = local_endpoint[0].get_cluster_cidr()

                    if len(remote_endpoint) > 0:
                        # multi-cluster remote cluster info
                        cluster_view['mc_network']['remote']['name'] = remote_endpoint[0].get_name()
                        cluster_view['mc_network']['remote']['public'] = remote_endpoint[0].get_public_ip()
                        cluster_view['mc_network']['remote']['gateway'] = remote_endpoint[0].get_gateway_ip()
                        cluster_view['mc_network']['remote']['service_cidr'] = remote_endpoint[0].get_service_cidr()
                        cluster_view['mc_network']['remote']['cluster_cidr'] = remote_endpoint[0].get_cluster_cidr()

            # cluster conditions
            conditions = component.get_conditions()

            for condition in conditions:
                condition_view = ClusterViewModel.get_condition_view_model()
                condition_view['condition'] = condition.get_condition()
                condition_view['status'] = condition.get_status()
                condition_view['message'] = condition.get_message()
                condition_view['updated'] = condition.get_update()
                cluster_view['conditions'].append(condition_view)
        else:
            cluster_view['state'] = ClusterStatus.UNAVAILABLE.value

        cluster_views.append(cluster_view)

    return cluster_views


def get_cluster_list_view(query_params: dict = None) -> dict:
    """
    get clusters view
    :param query_params: (dict)
    :return:
    (dict) cluster.view_model.cluster_list_view_model
    (dict) cluster.view_model.cluster_name_list_view_model
    """
    cluster_list_view = ClusterViewModel.get_cluster_list_view_model()

    # parse query params
    if query_params is not None and len(query_params.keys()) > 0:
        if 'filter' in query_params.keys():
            filter_name = query_params['filter']
            if filter_name == 'name':
                return get_cluster_name_list_view()
            else:
                raise ValueError(GSLinkManagerError.INVALID_QUERY_PARAM_VALUE.format(param='filter', val='name'))

    ok, items, error_message = \
        ClusterDAO.get_all_cluster_objects()

    if not ok:
        error = 'No entry for clusters in database, caused by ' + error_message
        logger.error(error)
        raise SystemError(error)

    cluster_list_view['clusters'] = get_cluster_views(items)

    return cluster_list_view


def get_cluster_component_condition_views(items: List[dict]) -> list:
    """
    get cluster component condition views
    :param items: list[cluster.model.Cluster]
    :return: list[cluster.view_model.cluster_component_condition_view_model]
    """
    cluster_component_condition_views = []

    if not items:
        return cluster_component_condition_views

    # fills cluster context
    for item in items:
        cluster_component_condition_view = ClusterViewModel.get_cluster_component_condition_view_model()
        cluster_component_condition_view['id'] = item.get('cluster_id', None)
        cluster_component_condition_view['name'] = item.get('cluster_name', None)

        # cluster info
        cache = ClusterCache().get_cluster(cluster_component_condition_view['name'])
        if cache:
            # get component status from cache
            component = cache['component']
            # cluster conditions
            conditions = component.get_conditions()

            for condition in conditions:
                condition_view = ClusterViewModel.get_condition_view_model()
                condition_view['condition'] = condition.get_condition()
                condition_view['status'] = condition.get_status()
                condition_view['message'] = condition.get_message()
                condition_view['updated'] = condition.get_update()
                cluster_component_condition_view['conditions'].append(condition_view)

        cluster_component_condition_views.append(cluster_component_condition_view)

    return cluster_component_condition_views


def get_cluster_component_condition_list_view(cluster_name: str) -> dict:
    """
    get cluster component condition list view for cluster name
    :param cluster_name: (str) cluster name
    :return: (dict) cluster.view_model.cluster_list_view_model
    """
    cluster_list_view = ClusterViewModel.get_cluster_list_view_model()

    # retrieve cluster data from database
    if cluster_name:
        ok, items, error_message = \
            ClusterDAO.get_cluster_objects_by_name(cluster_name)

        if not ok:
            error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
            logger.error(error)
            raise SystemError(error)

    else:  # retrieve all
        ok, items, error_message = \
            ClusterDAO.get_all_cluster_objects()

        if not ok:
            error = 'No entry for clusters in database, caused by ' + error_message
            logger.error(error)
            raise SystemError(error)

    cluster_list_view['clusters'] = get_cluster_component_condition_views(items)

    return cluster_list_view


def get_cluster_view(cluster_name: str) -> dict:
    """
    get cluster view for cluster name
    :param cluster_name: (str) cluster name
    :return: (dict) cluster.view_model.cluster_list_view_model
    """
    cluster_list_view = ClusterViewModel.get_cluster_list_view_model()

    if cluster_name is None:
        # If cluster name is null, returns null view model
        cluster_list_view['clusters'].append(ClusterViewModel.get_cluster_view_model())
        return cluster_list_view

    ok, items, error_message = \
        ClusterDAO.get_cluster_objects_by_name(cluster_name)

    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    cluster_list_view['clusters'] = get_cluster_views(items)

    return cluster_list_view


def delete_cluster(cluster_name: str, timeout: int=60) -> dict:
    """
    delete cluster registered
    :param cluster_name: (str) cluster name
    :param timeout: (int) await seconds
    :return: (cluster.view_model.cluster_deletion_view_model)
    """
    cluster_deletion_view = ClusterViewModel.get_cluster_deletion_view_model()

    ok, cluster_objects, error_message = \
        ClusterDAO.get_cluster_objects_by_name(cluster_name)

    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if len(cluster_objects) <= 0:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    ok, error_message = \
        ClusterDAO.delete_cluster(cluster_name)

    if not ok:
        error = 'Failed to delete cluster({}) entry, caused by {}'.format(cluster_name, error_message)
        logger.error(error)

        raise SystemError(error)

    # remove cluster in cluster cache
    cache = ClusterCache().get_cluster(cluster_name)

    if cache:
        ClusterCache().delete_cluster(cluster_name)

    # if cluster agent is connect, request to delete agent
    # if cache and cache['state'] == ClusterStatus.ACTIVE.value:
    #     request_id = ClusterAgent.remove_agent(cluster_id=cluster_name)
    #
    #     # wait until agent's response arrive(timeout: 60s)
    #     ok, stdout, stderr = RequestCache().wait(request_id, timeout)
    #     if not ok:
    #         if stderr == RequestCache.NOT_READY or stderr == RequestCache.REQUEST_NOT_CACHED:
    #             error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
    #             logger.error(error)
    #             raise SystemError(error)

    # fills cluster delete view
    cluster_deletion_view['id'] = cluster_objects[0]['cluster_id']
    cluster_deletion_view['name'] = cluster_objects[0]['cluster_name']
    cluster_deletion_view['result']['success'] = ok
    cluster_deletion_view['result']['stdout'] = ''
    cluster_deletion_view['result']['error'] = ''

    return cluster_deletion_view


def register_cluster(request_body: dict) -> dict:
    """
    register cluster
    :param request_body: (dict)
    :return: (dict) cluster.view_model.cluster_view_model
    """
    if request_body is None:
        raise KeyError(GSLinkManagerError.BODY_NOT_FOUND_ERROR)

    if 'name' not in request_body:
        raise KeyError(GSLinkManagerError.BODY_FIELD_NOT_FOUND_ERROR.format(field='name'))

    if type(request_body['name']) != str:
        raise ValueError(GSLinkManagerError.INVALID_BODY_FIELD_VALUE.format(field='name', val=request_body['name']))

    if not request_body['name']:
        raise ValueError(GSLinkManagerError.INVALID_BODY_FIELD_VALUE.format(field='name', val=request_body['name']))

    if 'description' not in request_body:
        return KeyError(GSLinkManagerError.BODY_FIELD_NOT_FOUND_ERROR.format(field='description'))

    ok, cluster, error_message = \
        ClusterDAO.register_cluster_object(cluster_name=request_body['name'],
                                           description=request_body['description'])
    if not ok:
        error = 'Failed in ClusterDAO.register_cluster_object(), cluster_name={}, ' \
                'caused by {}'.format(request_body['name'], error_message)
        logger.error(error)
        return SystemError(error)

    # fills cluster view for registered one
    cluster_view = ClusterViewModel.get_cluster_view_model()
    cluster_view['id'] = cluster.cluster_id
    cluster_view['name'] = cluster.cluster_name
    cluster_view['desc'] = cluster.description
    cluster_view['state'] = ClusterStatus.UNAVAILABLE.value
    cluster_view['api_address'] = None
    cluster_view['api_version'] = None
    cluster_view['registration'] = cluster.registration_command
    cluster_view['nodes'] = None
    cluster_view['mc_network'] = None
    cluster_view['conditions'] = []

    return cluster_view

def rollback_multi_cluster_connect_request(cluster_name: str, mc_connect_id: str):
    """
    rollback local broker connect request
    :param cluster_name: (str) cluster name
    :param mc_connect_id: (str) connect id
    :return:
    """
    request_id = \
        ClusterAgent.disconnect_multi_cluster_network(cluster_id=cluster_name,
                                                      connect_id=mc_connect_id)

    return RequestCache().wait(request_id, 60)


def connect_mc_network(cluster_name: str, request_body: dict, timeout: int=60):
    """
    connect multi-cluster network
    :param request_body: (dict)
    :param cluster_name: (str) cluster name
    :param timeout: (int) run timeout
    :return:
    """
    if not cluster_name or type(cluster_name) != str or len(cluster_name) <= 0:
        raise KeyError(GSLinkManagerError.INVALID_CLUSTER_NAME_ERROR.format(cluster=cluster_name))

    if 'target' not in request_body:
        raise KeyError(GSLinkManagerError.BODY_FIELD_NOT_FOUND_ERROR.format(field='target'))

    local_cluster_name = cluster_name
    remote_cluster_name = request_body['target']

    if not request_body['target'] or type(request_body['target']) != str or len(request_body['target']) <= 0:
        raise KeyError(GSLinkManagerError.INVALID_BODY_FIELD_VALUE.format(field='target', val=request_body['target']))

    # validate local cluster
    ok, local_cluster_objects, error_message = \
        ClusterDAO.get_cluster_objects_by_name(local_cluster_name)

    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not local_cluster_objects or len(local_cluster_objects) <= 0:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=local_cluster_name))

    local_cluster_id = local_cluster_objects[0].get('cluster_id', None)
    connected_id = local_cluster_objects[0].get('mc_connect_id', None)
    mc_config_state = local_cluster_objects[0].get('mc_config_state', None)

    if not local_cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=local_cluster_name))

    # check whether remote cluster is already connected
    if connected_id:
        raise ValueError(GSLinkManagerError.MULTI_CLUSTER_NETWORK_ALREADY_CONNECTED.format(cluster=local_cluster_name))

    if mc_config_state and (mc_config_state != Cluster.MultiClusterConfigState.NONE.value):
        raise ValueError(GSLinkManagerError.MULTI_CLUSTER_NETWORK_ALREADY_CONNECTED.format(cluster=local_cluster_name))

    # check local cluster agent is connected to center
    local_cluster_cache = ClusterCache().get_cluster(local_cluster_name)

    if not local_cluster_cache:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_CONNECTED_ERROR.format(cluster=local_cluster_name))

    if local_cluster_cache['state'] != ClusterStatus.ACTIVE.value:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_CONNECTED_ERROR.format(cluster=local_cluster_name))

    # validate remote cluster
    ok, remote_cluster_objects, error_message = \
        ClusterDAO.get_cluster_objects_by_name(remote_cluster_name)

    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not remote_cluster_objects or len(remote_cluster_objects) <= 0:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=remote_cluster_name))

    remote_cluster_id = remote_cluster_objects[0].get('cluster_id', None)
    connected_id = remote_cluster_objects[0].get('mc_connect_id', None)
    mc_config_state = remote_cluster_objects[0].get('mc_config_state', None)

    if not remote_cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=remote_cluster_name))

    # check whether remote cluster is already connected
    if connected_id:
        raise ValueError(GSLinkManagerError.MULTI_CLUSTER_NETWORK_ALREADY_CONNECTED.format(cluster=remote_cluster_name))

    if mc_config_state and (mc_config_state != Cluster.MultiClusterConfigState.NONE.value):
        raise ValueError(GSLinkManagerError.MULTI_CLUSTER_NETWORK_ALREADY_CONNECTED.format(cluster=remote_cluster_name))

    # check remote cluster agent is connected to center
    remote_cluster_cache = ClusterCache().get_cluster(remote_cluster_name)

    if not remote_cluster_cache:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_CONNECTED_ERROR.format(cluster=remote_cluster_name))

    if remote_cluster_cache['state'] != ClusterStatus.ACTIVE.value:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_CONNECTED_ERROR.format(cluster=remote_cluster_name))

    if not remote_cluster_cache:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_CONNECTED_ERROR.format(cluster=remote_cluster_name))

    """ check whether multi-cluster network is connectable for local cluster """
    request_id = ClusterAgent().get_broker_status(local_cluster_name)
    ok, stdout, stderr = RequestCache().wait(request_id, 60)

    if not ok or not stdout or len(stdout) <= 0:
        logger.error('Failed in ClusterAgent().get_broker_status(local_cluster_name),'
                     'caused by ' + stderr)

        raise ValueError(GSLinkManagerError.LOCAL_CLUSTER_BROKER_NOT_READY_ERROR.format(cluster=local_cluster_name))

    # agent request timeout
    if stderr == RequestCache.REQUEST_TIMEOUT:
        raise ValueError(GSLinkManagerError.BROKER_STATUS_REQUEST_TIMEOUT.format(cluster=local_cluster_name))

    local_submariner_status = stdout
    if local_submariner_status != SubmarinerState.BROKER_READY.value:
        raise ValueError(GSLinkManagerError.MULTI_CLUSTER_NETWORK_UNAVAILABLE.format(cluster=local_cluster_name))

    """ check whether multi-cluster network is connectable for remote cluster """
    request_id = ClusterAgent().get_broker_status(remote_cluster_name)
    ok, stdout, stderr = RequestCache().wait(request_id, 60)

    if not ok or not stdout or len(stdout) <= 0:
        logger.error('Failed in ClusterAgent().get_broker_status(remote_cluster_name),'
                     'caused by ' + stderr)

        raise ValueError(GSLinkManagerError.LOCAL_CLUSTER_BROKER_NOT_READY_ERROR.format(cluster=remote_cluster_name))

    # agent request timeout
    if stderr == RequestCache.REQUEST_TIMEOUT:
        raise ValueError(GSLinkManagerError.BROKER_STATUS_REQUEST_TIMEOUT.format(cluster=remote_cluster_name))

    remote_submariner_status = stdout
    if remote_submariner_status != SubmarinerState.BROKER_READY.value:
        raise ValueError(GSLinkManagerError.MULTI_CLUSTER_NETWORK_UNAVAILABLE.format(cluster=remote_cluster_name))

    """ get broker info file from local cluster """
    request_id = ClusterAgent().get_broker_info(local_cluster_name)

    ok, stdout, stderr = RequestCache().wait(request_id, 60)

    if not ok or not stdout or len(stdout) <= 0:
        logger.error('Failed in ClusterAgent().get_broker_info(local_cluster_name),'
                     'caused by ' + stderr)

        raise ValueError(GSLinkManagerError.LOCAL_CLUSTER_BROKER_NOT_READY_ERROR.format(val=local_cluster_name))

    # agent request timeout
    if stderr == RequestCache.REQUEST_TIMEOUT:
        raise ValueError(GSLinkManagerError.BROKER_INFO_REQUEST_TIMEOUT.format(cluster=local_cluster_name))

    local_broker_info = stdout

    """ generate connect_id """
    connect_id = str(uuid.uuid4())
    connection_result = {}

    """ request multi-cluster network connect for local broker """
    local_connect_request = \
        ClusterAgent.connect_multi_cluster_network(cluster_id=local_cluster_name,
                                                   mc_connect_id=connect_id,
                                                   role=MultiClusterRole.LOCAL.value,
                                                   remote_cluster_id=remote_cluster_name)

    ok, stdout, stderr = RequestCache().wait(local_connect_request, 60)

    if not ok:
        if stderr == RequestCache.NOT_READY or stderr == RequestCache.REQUEST_NOT_CACHED:
            error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
            logger.error(error)
            raise SystemError(error)

        logger.error('Failed in ClusterAgent.connect_multi_cluster_network(), '
                     'role=Local, cluster'+local_cluster_name)

        raise ConnectionError(
            GSLinkManagerError.MULTI_CLUSTER_CONNECT_FAIL.format(cluster=local_cluster_name, reason=stderr))

    # agent request timeout
    if stderr == RequestCache.REQUEST_TIMEOUT:
        raise ValueError(GSLinkManagerError.MULTI_CLUSTER_CONNECT_REQUEST_TIMEOUT.format(cluster=local_cluster_name))

    """ set view data """
    connection_result[local_connect_request] = {}
    connection_result[local_connect_request]['success'] = ok
    connection_result[local_connect_request]['result'] = stdout
    connection_result[local_connect_request]['error'] = stderr

    """ request multi-cluster network connect for remote broker """
    remote_connect_request = \
        ClusterAgent.connect_multi_cluster_network(cluster_id=remote_cluster_name,
                                                   role=MultiClusterRole.REMOTE.value,
                                                   mc_connect_id=connect_id,
                                                   remote_cluster_id=local_cluster_name,
                                                   broker_info_text=local_broker_info)

    # wait until all request are completed or timeout
    ok, stdout, stderr = RequestCache().wait(remote_connect_request, 60)

    if not ok:
        if stderr == RequestCache.NOT_READY or stderr == RequestCache.REQUEST_NOT_CACHED:
            rollback_multi_cluster_connect_request(
                cluster_name=local_cluster_name, mc_connect_id=connect_id)
            error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
            logger.error(error)
            raise SystemError(error)

        logger.error('Failed in ClusterAgent.connect_multi_cluster_network(), '
                     'role=Remote, cluster' + remote_cluster_name)

        raise ConnectionError(
            GSLinkManagerError.MULTI_CLUSTER_CONNECT_FAIL.format(v1=remote_cluster_name, v2=stderr))

    # agent request timeout
    if stderr == RequestCache.REQUEST_TIMEOUT:
        # rollback transaction
        rollback_multi_cluster_connect_request(cluster_name=local_cluster_name, mc_connect_id=connect_id)
        raise ValueError(GSLinkManagerError.MULTI_CLUSTER_CONNECT_REQUEST_TIMEOUT.format(cluster=local_cluster_name))

    # update connected_id to local cluster
    ok, error_message = ClusterDAO.update_multi_cluster_connection(
        cluster_name=local_cluster_name,
        mc_connect_id=connect_id,
        role=MultiClusterRole.LOCAL.value,
        mc_config_state=Cluster.MultiClusterConfigState.CONNECTING.value,
        broker_info=local_broker_info)

    if not ok:
        error = 'Failed in ClusterDAO.update_multi_cluster_connection(), ' \
                'cluster={} reason={}'.format(local_cluster_name, error_message)
        logger.error(error)

        # rollback transaction
        rollback_multi_cluster_connect_request(cluster_name=local_cluster_name, mc_connect_id=connect_id)
        rollback_multi_cluster_connect_request(cluster_name=remote_cluster_name, mc_connect_id=connect_id)

        raise  SystemError(error)

    # update connected_id to remote cluster
    ok, error_message = ClusterDAO.update_multi_cluster_connection(
        cluster_name=remote_cluster_name,
        mc_connect_id=connect_id,
        role=MultiClusterRole.REMOTE.value,
        mc_config_state=Cluster.MultiClusterConfigState.CONNECTING.value,
        broker_info=local_broker_info)

    if not ok:
        error = 'Failed in ClusterDAO.update_multi_cluster_connection(), ' \
                'cluster={} reason={}'.format(remote_cluster_name, error_message)
        logger.error(error)

        # rollback transaction
        rollback_multi_cluster_connect_request(cluster_name=local_cluster_name, mc_connect_id=connect_id)
        rollback_multi_cluster_connect_request(cluster_name=remote_cluster_name, mc_connect_id=connect_id)

        ClusterDAO.update_multi_cluster_connection(
            cluster_name=local_cluster_name,
            mc_connect_id=None,
            role=MultiClusterRole.NONE.value,
            mc_config_state=Cluster.MultiClusterConfigState.NONE.value,
            broker_info=local_broker_info)

        raise SystemError(error)

    # create view
    mc_network_control_view = ClusterViewModel.get_mc_network_control_view_model()
    mc_network_control_view['id'] = local_cluster_id
    mc_network_control_view['name'] = cluster_name
    mc_network_control_view['error'] = None

    return mc_network_control_view


def disconnect_mc_network(cluster_name: str, timeout: int=60):
    """
    disconnect multi-cluster network
    :param cluster_name: (str) cluster name
    :param timeout: (int) await seconds
    :return:
    """
    # validate local cluster
    ok, cluster_objects, error_message = ClusterDAO.get_cluster_objects_by_name(cluster_name)

    # database error
    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    # cluster not found error
    if not cluster_objects or len(cluster_objects) <= 0:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    selected_cluster_object = cluster_objects[0]
    cluster_id = selected_cluster_object.get('cluster_id', None)
    connect_id = selected_cluster_object.get('mc_connect_id', None)
    mc_config_state = selected_cluster_object.get('mc_config_state', None)

    # If cluster config state is not 'Connected', returns "disconnect refused" error
    if mc_config_state != Cluster.MultiClusterConfigState.CONNECTED.value:
        raise ValueError(GSLinkManagerError.MULTI_CLUSTER_DISCONNECT_REFUSED.format(cluster=cluster_name,
                                                                                    state=mc_config_state))

    # cluster id not found error for selected cluster
    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_ID_NOT_FOUND_ERROR.format(cluster=cluster_name))

    # multi-cluster id not found error for selected cluster
    if not connect_id:
        raise ValueError(GSLinkManagerError.NOT_CONNECTED_MC_NETWORK.format(cluster=cluster_name))

    # get all cluster with mc_connect_id
    ok, cluster_objects, error_message = \
        ClusterDAO.get_cluster_objects_by_connected_id(mc_connect_id=connect_id)

    # database error
    if not ok:
        error = 'Failed in ClusterDAO.get_cluster_objects_by_connected_id(mc_connect_id=connect_id), ' \
                'mc_connect_id={}, caused by {}'.format(connect_id, error_message)
        logger.error(error)
        raise SystemError(error)

    # cluster not found error
    if not cluster_objects:
        error = 'Failed in ClusterDAO.get_cluster_objects_by_connected_id(mc_connect_id=connect_id), ' \
                'mc_connect_id={}, caused by {}'.format(connect_id, 'cluster not found in Database')
        logger.error(error)
        raise SystemError(error)

    connected_cluster_object = None

    # find connected cluster object with cluster_name
    for cluster_object in cluster_objects:
        val = cluster_object.get('cluster_name', None)

        if val and val != cluster_name:
            connected_cluster_object = cluster_object
            break


    # cluster not found for connected cluster
    if not connected_cluster_object:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    mc_config_state = connected_cluster_object.get('mc_config_state', None)
    connected_cluster_name = connected_cluster_object.get('cluster_name', None)

    # cluster not found error
    if not connected_cluster_name:
        error = GSLinkManagerError.MULTI_CLUSTER_CONNECTED_REMOTE_CLUSTER_NOT_FOUND.format(cluster=connected_cluster_name)
        logger.error(error)
        raise ValueError(error)

    # If cluster config state is not 'Connected', returns "disconnect refused" error
    if mc_config_state != Cluster.MultiClusterConfigState.CONNECTED.value:
        raise ValueError(GSLinkManagerError.MULTI_CLUSTER_DISCONNECT_REFUSED.format(cluster=connected_cluster_name,
                                                                                    state=mc_config_state))
    # update mc-config-state to "Disconnecting" for selected cluster
    ok, error_message = ClusterDAO.update_multi_cluster_connection(
        cluster_name=selected_cluster_object.get('cluster_name', None),
        mc_connect_id=selected_cluster_object.get('mc_connect_id', None),
        role=selected_cluster_object.get('role', None),
        mc_config_state=Cluster.MultiClusterConfigState.DISCONNECT_PENDING.value,
        broker_info=selected_cluster_object.get('broker_info', None))

    # database error
    if not ok:
        error = 'Failed in ClusterDAO.update_multi_cluster_connection. caused by ' + error_message
        logger.error(error)
        raise SystemError(error)

    # update mc-config-state to "Disconnecting" for connected cluster
    ok, error_message = ClusterDAO.update_multi_cluster_connection(
        cluster_name=connected_cluster_object.get('cluster_name', None),
        mc_connect_id=connected_cluster_object.get('mc_connect_id', None),
        role=connected_cluster_object.get('role', None),
        mc_config_state=Cluster.MultiClusterConfigState.DISCONNECT_PENDING.value,
        broker_info=connected_cluster_object.get('broker_info', None))

    # database error
    if not ok:
        error = 'Failed in ClusterDAO.update_multi_cluster_connection. caused by ' + error_message
        logger.error(error)
        raise SystemError(error)

    # create view
    mc_network_control_view = ClusterViewModel.get_mc_network_control_view_model()
    mc_network_control_view['id'] = cluster_id
    mc_network_control_view['name'] = cluster_name
    mc_network_control_view['error'] = None

    return mc_network_control_view

# deprecated, 23-11-13
# def get_mc_network_latency_view(cluster_name: str) -> dict:
#     """
#     get multicluster network latency view
#     :param cluster_name: (str) cluster name
#     :return: (dict) cluster.view_model.mc_network_latency_view
#     """
#     mc_network_latency_view = ClusterViewModel.get_mc_network_latency_view_model()
#
#     if cluster_name is None:
#         return mc_network_latency_view
#
#     ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)
#
#     if not ok:
#         error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
#         logger.error(error)
#         raise SystemError(error)
#
#     if not cluster_id:
#         raise ValueError(GSLinkManagerError.CLUSTER_ID_NOT_FOUND_ERROR.format(cluster=cluster_name))
#
#     cache = ClusterCache().get_cluster(cluster_name)
#
#     if cache:
#         metric = cache['metric']
#         mc_network_metric = metric.get_mc_network()
#         endpoint_metric = mc_network_metric.get_endpoint_metric(cluster_name)
#
#         if not endpoint_metric:
#             return mc_network_latency_view
#
#         mc_network_latency_view['latency'] = endpoint_metric.latency
#         mc_network_latency_view['latency_measure_date'] = endpoint_metric.latency_measure_date
#
#     return mc_network_latency_view


def get_mc_network_metric_view(cluster_name: str, endpoint_name: str) -> dict:
    """
    get multicluster network throughput view
    :param cluster_name: (str) cluster name
    :param endpoint_name: (str) endpoint cluster name
    :return: (dict) cluster.view_model.get_mc_network_metric_view_model
    """
    mc_network_metric_view = ClusterViewModel.get_mc_network_metric_view_model()

    if cluster_name is None:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    if endpoint_name is None:
        return ValueError(GSLinkManagerError.ENDPOINT_NOT_FOUND_ERROR.format(endpoint=endpoint_name))

    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)

    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_ID_NOT_FOUND_ERROR.format(cluster=cluster_name))

    cache = ClusterCache().get_cluster(cluster_name)

    if cache:
        metric = cache['metric']
        mc_network_metric = metric.get_mc_network()
        endpoint_metric = mc_network_metric.get_endpoint_metric(endpoint_name)

        if not endpoint_metric:
            return mc_network_metric_view

        mc_network_metric_view['latencies'] = endpoint_metric.get_latencies()
        mc_network_metric_view['tx_bytes'] = endpoint_metric.get_tx_bytes()
        mc_network_metric_view['rx_bytes'] = endpoint_metric.get_rx_bytes()

    return mc_network_metric_view


def get_node_view(node: Node, running_pods: int) -> dict:
    """
    get node view
    :param node: (repository.model.k8s.node.Node)
    :param running_pods: (int) running pod in the node
    :return: (dict) cluster.view_model.node_view_model
    """
    node_view = ClusterViewModel.get_node_view_model()
    node_view['name'] = node.get_name()
    node_view['state'] = node.get_state()
    node_view['ip'] = node.get_ip()
    node_view['host_if'] = node.get_iface()
    node_view['role'] = node.get_role()
    k8s_version_abb = None
    if node.get_k8s_version():
        k8s_version_abb = node.get_k8s_version().split('-')[0]
    node_view['k8s_version'] = k8s_version_abb
    node_view['os'] = node.get_os()
    node_view['number_of_cpu'] = node.get_number_of_cpu()
    ram_size = ""
    val = node.get_ram_size()
    val = val.split('Ki')[0]

    if val:
        if Validator.is_enable_cast_to_int(val):
            val = float(val)
            val = val / 1024 / 1024   # Gi
            ram_size = "{:.2f} Gi".format(val)

    node_view['ram_size'] = ram_size
    max_pods_string = node.get_max_pods()
    node_view['pods']['max_pods'] = max_pods_string
    node_view['pods']['running_pods'] = running_pods

    if Validator.is_enable_cast_to_int(max_pods_string):
        max_pods = int(max_pods_string)
    else:
        max_pods = -1

    if running_pods > 0 and max_pods > 0:
        node_view['pods']['usage'] = \
            '{:.2f}'.format(running_pods / max_pods * 100)
    else:
        node_view['pods']['usage'] = '0.0'

    node_view['stime'] = node.get_stime()
    node_view['age'] = DateFormatter.get_age(node.get_stime())

    return node_view

def get_nodes_view(cluster_name: str,
                   node_name: str = None) -> dict:
    """
    get nodes view
    :param cluster_name: (str) cluster name
    :param node_name: (str) node name
    :return: (cluster.view_model.node_list_view_model)
    """
    node_list_view = ClusterViewModel.get_node_list_view_model()

    if cluster_name is None:
        return node_list_view

    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)

    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_ID_NOT_FOUND_ERROR.format(cluster=cluster_name))

    node_list_view['name'] = cluster_name
    node_list_view['id'] = cluster_id

    cache = ClusterCache().get_cluster(cluster_name)

    if cache:
        resource = cache['resource']
        nodes = resource.get_nodes()

        # iterate node in cache and create node view
        if node_name:
            for node in nodes:
                if node_name == node.get_name():
                    running_pods = resource.get_number_of_pods(node_name)
                    node_view = get_node_view(node, running_pods)
                    node_list_view['nodes'].append(node_view)
        else:
            for node in nodes:
                running_pods = resource.get_number_of_pods(node.get_name())
                node_view = get_node_view(node, running_pods)
                node_list_view['nodes'].append(node_view)

    return node_list_view


def get_node_metrics_view(cluster_name: str,
                          node_name: str) -> dict:
    """
    get metrics for all registered nodes
    :param cluster_name: (str) cluster name
    :param node_name: (str) node name
    :return: (dict) cluster.view_model.node_metric_list_view_model
    """
    node_metric_list_view = ClusterViewModel.get_node_metric_list_view_model()

    if cluster_name is None:
        return node_metric_list_view

    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)

    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_ID_NOT_FOUND_ERROR.format(cluster=cluster_name))

    node_metric_list_view['name'] = cluster_name
    node_metric_list_view['id'] = cluster_id

    if node_name is None:
        return node_metric_list_view

    cache = ClusterCache().get_cluster(cluster_name)

    if cache:
        metric = cache['metric']
        resource = cache['resource']

        node_metric = metric.get_node(node_name)

        if not node_metric:
            return node_metric_list_view

        node_status = resource.get_node(node_name)

        if not node_status:
            return node_metric_list_view

        node_metric_view = ClusterViewModel.get_node_metric_view_model()
        node_metric_view['name'] = node_metric.get_name()
        running_pods = resource.get_number_of_pods(node_name)
        max_pods_string = node_status.get_max_pods()
        node_metric_view['pods']['running_pods'] = running_pods
        node_metric_view['pods']['max_pods'] = max_pods_string

        if Validator.is_enable_cast_to_int(max_pods_string):
            max_pods = int(max_pods_string)
        else:
            max_pods = -1

        if running_pods > 0 and max_pods > 0:
            node_metric_view['pods']['usage']= \
                '{:.2f}'.format(running_pods / max_pods * 100)
        else:
            node_metric_view['pods']['usage'] = '0.0'

        # cpu usage
        cpu_metric = node_metric.get_cpu_metric()
        node_metric_view['cpu_total'] = cpu_metric.total
        node_metric_view['cpu_usages'] = cpu_metric.usages

        # memory usage
        memory_metric = node_metric.get_memory_metric()
        node_metric_view['mem_total'] = memory_metric.total
        node_metric_view['mem_usages'] = memory_metric.usages

        # network usages
        network_metric = node_metric.get_network_metric()

        node_metric_view['net_tx_bytes'] = network_metric.tx_bytes
        node_metric_view['net_rx_bytes'] = network_metric.rx_bytes

        node_metric_list_view['nodes'].append(node_metric_view)

    return node_metric_list_view

def apply_manifest(cluster_name: str,
                   request_body: dict,
                   timeout: int = 60) -> dict:
    """
    apply resource manifest
    :param cluster_name: (str) cluster name
    :param request_body: (dict)
    :param timeout: (int) await seconds
    :return: (dict) cluster.view_model.resource_manifest_control_view_model
    """
    if request_body is None:
        raise KeyError(GSLinkManagerError.BODY_NOT_FOUND_ERROR)

    if 'manifest' not in request_body:
        raise KeyError(GSLinkManagerError.BODY_FIELD_NOT_FOUND_ERROR.format(field='manifest'))

    manifest_content = request_body['manifest']

    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)

    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_ID_NOT_FOUND_ERROR.format(cluster=cluster_name))

    # run delete daemonset from agent
    filename = str(uuid.uuid4()) + '.yaml'
    request_id = ClusterAgent.apply_resource_manifest_stream(cluster_id=cluster_name,
                                                             buffer=manifest_content,
                                                             filename=filename)

    # wait until agent's response arrive(timeout: 60s)
    ok, stdout, stderr = RequestCache().wait(request_id, timeout)
    if not ok:
        if stderr == RequestCache.NOT_READY or stderr == RequestCache.REQUEST_NOT_CACHED:
            error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
            logger.error(error)
            raise SystemError(error)

    control_resource_manifest_view = ClusterViewModel.get_resource_manifest_control_view_model()
    control_resource_manifest_view['name'] = cluster_name
    control_resource_manifest_view['id'] = cluster_id
    control_resource_manifest_view['result']['success'] = ok
    control_resource_manifest_view['result']['stdout'] = stdout
    control_resource_manifest_view['result']['error'] = stderr

    return control_resource_manifest_view


def delete_manifest(cluster_name: str,
                    request_body: dict,
                    timeout: int = 60) -> dict:
    """
    delete resource manifest
    :param cluster_name: (str) cluster name
    :param request_body: (dict)
    :param timeout: (int) await seconds
    :return: (dict) cluster.view_model.resource_manifest_control_view_model
    """
    if request_body is None:
        raise KeyError(GSLinkManagerError.BODY_NOT_FOUND_ERROR)

    if 'manifest' not in request_body:
        raise KeyError(GSLinkManagerError.BODY_FIELD_NOT_FOUND_ERROR.format(field='manifest'))

    manifest_content = request_body['manifest']

    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)
    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_ID_NOT_FOUND_ERROR.format(cluster=cluster_name))

    # run delete daemonset from agent
    filename = str(uuid.uuid4()) + '.yaml'
    request_id = ClusterAgent.delete_resource_manifest_stream(cluster_id=cluster_name,
                                                              buffer=manifest_content,
                                                              filename=filename)

    # wait until agent's response arrive(timeout: 60s)
    ok, stdout, stderr = RequestCache().wait(request_id, timeout)
    if not ok:
        if stderr == RequestCache.NOT_READY or stderr == RequestCache.REQUEST_NOT_CACHED:
            error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
            logger.error(error)
            raise SystemError(error)

    control_resource_manifest_view = ClusterViewModel.get_resource_manifest_control_view_model()
    control_resource_manifest_view['name'] = cluster_name
    control_resource_manifest_view['id'] = cluster_id
    control_resource_manifest_view['result']['success'] = ok
    control_resource_manifest_view['result']['stdout'] = stdout
    control_resource_manifest_view['result']['error'] = stderr

    return control_resource_manifest_view


def validate_manifest(cluster_name: str,
                      request_body: dict,
                      timeout: int = 60) -> dict:
    """
    validate resource manifest
    :param cluster_name: (str) cluster name
    :param request_body: (dict)
    :param timeout: (int) await seconds
    :return: (dict) cluster.view_model.resource_manifest_control_view_model
    """
    if request_body is None:
        raise KeyError(GSLinkManagerError.BODY_NOT_FOUND_ERROR)

    if 'manifest' not in request_body:
        raise KeyError(GSLinkManagerError.BODY_FIELD_NOT_FOUND_ERROR.format(field='manifest'))

    manifest_content = request_body['manifest']

    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)
    if not ok:
        error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_ID_NOT_FOUND_ERROR.format(cluster=cluster_name))

    # run delete daemonset from agent
    filename = str(uuid.uuid4()) + '.yaml'
    request_id = ClusterAgent.validate_resource_manifest_stream(cluster_id=cluster_name,
                                                                buffer=manifest_content,
                                                                filename=filename)

    # wait until agent's response arrive(timeout: 60s)
    ok, stdout, stderr = RequestCache().wait(request_id, timeout)
    if not ok:
        if stderr == RequestCache.NOT_READY or stderr == RequestCache.REQUEST_NOT_CACHED:
            error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
            logger.error(error)
            raise SystemError(error)

    control_resource_manifest_view = ClusterViewModel.get_resource_manifest_control_view_model()
    control_resource_manifest_view['name'] = cluster_name
    control_resource_manifest_view['id'] = cluster_id
    control_resource_manifest_view['result']['success'] = ok
    control_resource_manifest_view['result']['stdout'] = stdout
    control_resource_manifest_view['result']['error'] = stderr

    return control_resource_manifest_view

def diagnose_multi_cluster_network_failure(cluster_name: str) -> dict:
    """
    diagnose multi-cluster network failure
    :param cluster_name: (str) diagnosis cluster name
    :return: (dict) cluster.view_model.ClusterViewModel.get_diagnose_multi_cluster_network_failure_view_model
    """
    if not cluster_name or type(cluster_name) != str or len(cluster_name) <= 0:
        error_message = 'Invalid param. cluster_name=' + cluster_name
        logger.warn(error_message)
        raise ValueError(error_message)

    ok, mc_connect_id, error_message = \
        ClusterDAO.get_mc_connect_id(cluster_name=cluster_name)

    if not ok:
        error = 'Failed in ClusterDAO.get_mc_connect_id(cluster_name), caused by ' + error_message
        logger.error(error)
        raise SystemError(error)

    if not mc_connect_id:
        raise ValueError('Not found mc_connect_id. mc_connect_id=' + mc_connect_id)

    ok, cluster_objects, error_message = \
        ClusterDAO.get_cluster_objects_by_connected_id(mc_connect_id=mc_connect_id)

    if not ok:
        error = 'Failed in ClusterDAO.get_cluster_objects_by_connected_id(mc_connect_id=mc_connect_id), ' \
                'caused by ' + error_message
        logger.error(error)
        raise SystemError(error)

    source_cluster_object = None
    target_cluster_object = None

    for cluster_object in cluster_objects:
        cluster_name_saved = cluster_object.get('cluster_name', None)

        if cluster_name_saved != cluster_name:
            target_cluster_object = cluster_object
        else:
            source_cluster_object = cluster_object

    if not source_cluster_object:
        error = 'Not found source cluster in database. source cluster_name=' + cluster_name
        logger.error(error)
        raise SystemError(error)

    if not target_cluster_object:
        error = 'Not found target cluster in database. source cluster_name=' + cluster_name
        logger.error(error)
        raise SystemError(error)

    target_cluster_name = target_cluster_object['cluster_name']
    target_broker_info = target_cluster_object['broker_info']
    source_cluster_role = source_cluster_object['role']
    cache = ClusterCache().get_cluster(target_cluster_name)

    # check network connection status between center and target cluster's agent
    if not cache or cache['state'] != ClusterStatus.ACTIVE.value:
        diagnosis_status = MultiClusterNetworkDiagnosis.AGENT_NETWORK_ERROR.value

    else:
        # if request cluster's role is remote
        if source_cluster_role == MultiClusterRole.REMOTE.value:
            request_id = ClusterAgent.get_broker_info(target_cluster_name)
            ok, stdout, stderr = RequestCache().wait(request_id, 60)

            if not ok:
                error = 'Failed in ClusterAgent.get_broker_info(target_cluster_name), ' \
                        'caused by ' + error_message
                logger.error(error)
                raise SystemError(error)

            if not stdout or len(stdout) <= 0:
                error = 'Not found target cluster broker info'
                logger.error(error)
                raise SystemError(error)

            # # compare broker-info.subm checksum between center stored and cluster's response
            # v1 = MD5Checksum.get_checksums(target_broker_info)
            # v2 = MD5Checksum.get_checksums(stdout)

            if target_broker_info != stdout:
                diagnosis_status = MultiClusterNetworkDiagnosis.BROKER_UPDATED.value
                ok, error_message = ClusterDAO.update_cluster_broker_info(cluster_name=target_cluster_name,
                                                                          broker_info_content=stdout)
                if not ok:
                    logger.error('Failed in ClusterDAO.update_cluster_broker_info.'
                                 'caused by '+error_message)
            else:
                diagnosis_status = MultiClusterNetworkDiagnosis.MULTI_CLUSTER_NETWORK_ERROR.value

        else:
            # otherwise
            diagnosis_status = MultiClusterNetworkDiagnosis.MULTI_CLUSTER_NETWORK_ERROR.value

    # create view
    diagnose_multi_cluster_network_failure_view = \
        ClusterViewModel.get_diagnose_multi_cluster_network_failure_view_model()

    diagnose_multi_cluster_network_failure_view['cluster_name'] = cluster_name
    diagnose_multi_cluster_network_failure_view['result'] = diagnosis_status

    return diagnose_multi_cluster_network_failure_view


def get_join_broker_info(mc_connect_id: str) -> dict:
    """
    get join broker info
    :param mc_connect_id: (str) multi-cluster connection id
    :return: (dict) cluster.view_model.ClusterViewModel.get_join_broker_info_view_model
    """

    if not mc_connect_id or type(mc_connect_id) != str or len(mc_connect_id) <= 0:
        error_message = 'Invalid param. mc_connect_id=' + mc_connect_id
        logger.warn(error_message)
        raise ValueError(error_message)

    # get join broker-info.subm with multi-cluster member
    ok, cluster_objects, error_message = ClusterDAO.get_cluster_objects_by_connected_id(mc_connect_id)

    if not ok:
        error = 'Failed in ClusterDAO.get_cluster_objects_by_connected_id(mc_connect_id), ' \
                'caused by ' + error_message
        logger.error(error)
        raise SystemError(error)

    if len(cluster_objects) <= 0:
        raise ValueError('Not found connection')

    broker_info_content = cluster_objects[0].get('broker_info', None)

    if not broker_info_content:
        error = 'Not found broker info'
        logger.error(error)
        raise SystemError(error)

    # create view
    join_broker_info_view = ClusterViewModel.get_join_broker_info_view_model()
    join_broker_info_view['mc_connect_id'] = mc_connect_id
    join_broker_info_view['result'] = broker_info_content

    return join_broker_info_view

def get_gw_agent(cluster: str):
    """
    get gw agent
    :param cluster: (str) cluster name
    :return:
    """
    # validate cluster name
    if not cluster or type(cluster) != str or len(cluster) <= 0:
        error_message = 'Invalid param. cluster_name=' + cluster
        logger.warn(error_message)
        raise ValueError(error_message)

    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster)

    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster, error_message)
        logger.error(error)
        raise ValueError(GSLinkManagerError.CLUSTER_ID_NOT_FOUND_ERROR.format(cluster=cluster))

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_ID_NOT_FOUND_ERROR.format(cluster=cluster))

    bash_temp_dir = settings.BASH_TEMPLATE_DIRECTORY
    template_file = os.path.join(bash_temp_dir, 'gw_agent_template.sh')
    script_template = FileUtil.read_text_file(template_file)

    install_script = script_template.format(
        cluster=cluster,
        manager_ip=Configure().get_host(),
        agent_port=int(Configure().get_agent_port()),
        manager_port=int(Configure().get_http_port()),
        amqp_ip=Configure().get_host(),
        amqp_port=30001
    )

    return install_script
