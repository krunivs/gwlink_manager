from typing import List

from cache.request_cache import RequestCache
from gwlink_manager import settings
from gwlink_manager.common.error import GSLinkManagerError
from cluster.data_access_object import ClusterDAO
from repository.cache.cluster import ClusterCache
from repository.cache.network import NetworkStatusCache
from repository.model.k8s.condition import Condition
from repository.model.k8s.service import Service
from service.view_model import *
from utils.dateformat import DateFormatter
from mqtt.api import ClusterAgent

logger = settings.get_logger(__name__)


def get_condition_views(conditions: List[Condition]):
    """
    get condition list view
    :param conditions: (list[repository.model.k8s.condition.Condition])
    :return: (list[workloads.view_model.condition_view_model])
    """
    condition_views = []

    for condition in conditions:
        condition_view = ServiceViewModel.get_condition_view_model()
        condition_view['condition'] = condition.get_condition()
        condition_view['status'] = condition.get_status()
        condition_view['message'] = condition.get_message()
        condition_view['updated'] = DateFormatter.get_age(condition.get_update())
        condition_views.append(condition_view)

    return condition_views


def get_service_views(services: List[Service],
                      local_cluster_name: str,
                      remote_cluster_name: str,
                      remote_network_status: NetworkStatusCache) -> List[dict]:
    """
    get service view for service list
    :param services: (List[repository.model.k8s.service.Service])
    :param local_cluster_name: (str)
    :param remote_cluster_name: (str)
    :param remote_network_status: (repository.cache.network)
    :return: (List[dict]) list[service.view_model.service_view_model]
    """
    service_views = []

    if not services or len(services) <= 0:
        return service_views

    for service in services:
        service_view = ServiceViewModel.get_service_view_model()
        service_name = service.get_name()
        service_namespace = service.get_namespace()

        service_view['name'] = service_name
        service_view['state'] = service.get_state()
        service_view['namespace'] = service_namespace
        service_view['service_type'] = service.get_service_type()
        service_view['cluster_ip'] = service.get_cluster_ip()
        service_view['external_ips'] = service.get_external_ips()
        service_view['selector'] = service.get_selector()

        # ports
        ports = service.get_ports()
        for item in ports:
            port_view = ServiceViewModel.get_port_view_model()
            port_view['name'] = item.get_name()
            port_view['port'] = item.get_port()
            port_view['node_port'] = item.get_node_port()
            port_view['target_port'] = item.get_target_port()
            port_view['protocol'] = item.get_protocol()
            service_view['ports'].append(port_view)

        service_view['conditions'] = get_condition_views(service.get_conditions())
        service_view['stime'] = DateFormatter.get_age(service.get_stime())

        # service import from connected cluster
        service_export_view = ServiceViewModel.get_service_export_view_model()

        if remote_cluster_name is None or remote_network_status is None:
            service_export_view['status'] = 'false'
            service_export_view['reason'] = \
                GSLinkManagerError.MULTI_CLUSTER_NETWORK_UNAVAILABLE.format(cluster=local_cluster_name)
            service_export_view['clusterset_ip'] = ''
            service_export_view['service_discovery'] = ''
            service_export_view['stime'] = ''

        else:
            service_import = remote_network_status.get_imported_service(service_namespace, service_name)
            if service_import is not None:
                service_export_view['status'] = 'true'
                service_export_view['target'] = remote_cluster_name
                service_export_view['reason'] = ''
                service_export_view['clusterset_ip'] = service_import.get_ip()
                service_export_view['service_discovery'] = service_import.get_dns()
                service_export_view['stime'] = ''
            else:
                service_export_view['status'] = 'false'
                service_export_view['target'] = remote_cluster_name
                service_export_view['reason'] = GSLinkManagerError.SERVICE_NOT_EXPORTED
                service_export_view['clusterset_ip'] = ''
                service_export_view['service_discovery'] = ''
                service_export_view['stime'] = ''

        service_view['service_export'] = service_export_view
        service_views.append(service_view)

    return service_views


def get_service_list_view(cluster_name: str,
                          namespace: str,
                          query_params: dict = None) -> dict:
    """
    get deployment list view
    :param cluster_name: (str) cluster name
    :param namespace: (str) namespace name
    :param query_params: (dict)
    :return: (dict) service.view_model.service_list_view_model
    """
    # parse query params
    filter_key = None
    filter_value = None
    has_filter = False

    if query_params is not None and len(query_params.keys()) > 0:
        if len(query_params.keys()) != 1:
            raise KeyError('Query parameter should must be only one of the [pod]')
        if 'pod' in query_params.keys():
            filter_key = 'pod'
            filter_value = query_params['pod']
            has_filter = True
        else:
            raise KeyError('Query parameter should must be only one of the [pod]')

    service_list_view = ServiceViewModel.get_service_list_view_model()

    if cluster_name is None:
        return service_list_view

    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)
    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    service_list_view['name'] = cluster_name
    service_list_view['id'] = cluster_id

    cache = ClusterCache().get_cluster(cluster_name)

    if cache:
        resource = cache['resource']
        network = cache['network']

        remote_cluster_name = network.get_remote_mc_network_name()
        remote_cache = ClusterCache().get_cluster(remote_cluster_name)

        if remote_cache is not None:
            remote_network_status = remote_cache['network']
        else:
            remote_network_status = None

        if has_filter:  # filtered by pod
            if filter_key == 'pod':
                if namespace == '_all_':
                    services = resource.get_all_namespace_services_by_pod(filter_value)
                else:
                    services = resource.get_namespace_services_by_pod(namespace, filter_value)
            else:
                error = 'Invalid filter option. Only support one of the [pod]'
                logger.error(error)
                raise SystemError(error)
        else:
            if namespace == '_all_':
                services = resource.get_all_namespace_services()
            else:
                services = resource.get_namespace_services(namespace)

        service_list_view['services'] = get_service_views(services,
                                                          cluster_name,
                                                          remote_cluster_name,
                                                          remote_network_status)

    return service_list_view


def get_service_view(cluster_name: str,
                     namespace: str,
                     service_name: str) -> dict:
    """
    get service view
    :param cluster_name: (str) cluster name
    :param namespace: (str) namespace name
    :param service_name: (str) service name
    :return: (dict) workload.view_model.service_list_view_model
    """
    service_list_view = ServiceViewModel.get_service_list_view_model()
    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)

    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    service_list_view['name'] = cluster_name
    service_list_view['id'] = cluster_id

    cache = ClusterCache().get_cluster(cluster_name)

    if cache:
        resource = cache['resource']
        network = cache['network']

        remote_cluster_name = network.get_remote_mc_network_name()
        remote_cache = ClusterCache().get_cluster(remote_cluster_name)

        if remote_cache is not None:
            remote_network_status = remote_cache['network']
        else:
            remote_network_status = None

        if namespace == '_all_':
            services = resource.get_all_namespace_services_by_service(service_name)
            # get service export
        else:
            services = resource.get_namespace_services_by_service(namespace, service_name)
            # get service export

        service_list_view['services'] = get_service_views(services,
                                                          cluster_name,
                                                          remote_cluster_name,
                                                          remote_network_status)

    return service_list_view


def delete_service(cluster_name: str,
                   namespace: str,
                   service_name: str,
                   timeout: int = 60) -> dict:
    """
    delete service
    :param cluster_name: (str) cluster name
    :param namespace:  (str) namespace name
    :param service_name: (str) service name
    :param timeout: (int) await seconds
    :return: (dict) service.view_model.service_deletion_view_model
    """
    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)
    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    # run delete service from agent
    request_id = ClusterAgent.delete_service(cluster_id=cluster_name,
                                             namespace=namespace,
                                             service=service_name)

    # wait until agent's response arrive(timeout: 60s)
    ok, stdout, stderr = RequestCache().wait(request_id, timeout)
    if not ok:
        if stderr == RequestCache.NOT_READY or stderr == RequestCache.REQUEST_NOT_CACHED:
            error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
            logger.error(error)
            raise SystemError(error)

    service_deletion_view = ServiceViewModel.get_service_deletion_view_model()
    service_deletion_view['name'] = cluster_name
    service_deletion_view['id'] = cluster_id
    service_deletion_view['namespace'] = namespace
    service_deletion_view['service'] = service_name
    service_deletion_view['result']['success'] = ok
    service_deletion_view['result']['error'] = stderr
    service_deletion_view['result']['stdout'] = stdout

    return service_deletion_view


def do_export_service(cluster_name: str,
                      namespace_name: str,
                      service_name: str,
                      timeout: int = 60) -> dict:
    """
    export service
    :param cluster_name: (str) cluster name
    :param namespace_name: (str) namespace name
    :param service_name: (str) service name
    :param timeout: (int) await seconds
    :return: (dict) service.view_model.do_service_export_view_model
    """
    ok, cluster_objects, error_message = ClusterDAO.get_cluster_objects_by_name(cluster_name)

    if not ok or not cluster_objects:
        logger.error(error_message)
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    # check whether request cluster is connected or not
    cache = ClusterCache().get_cluster(cluster_name)
    if not cache:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_CONNECTED_ERROR.format(cluster=cluster_name))

    # check request service is exist or not
    resource = cache['resource']
    services = resource.get_namespace_services_by_service(namespace=namespace_name,
                                                          service=service_name)

    if not services or services[0].get_name() != service_name:
        raise ValueError(GSLinkManagerError.SERVICE_NOT_FOUND_ERROR.format(service=service_name))

    cluster_object = cluster_objects[0]
    cluster_id = cluster_object.get('cluster_id', None)
    connect_id = cluster_object.get('mc_connect_id', None)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    if not connect_id:
        raise ValueError(GSLinkManagerError.NOT_CONNECTED_MC_NETWORK.format(cluster=cluster_name))

    # get all cluster with mc_connect_id
    ok, cluster_objects, error_message = \
        ClusterDAO.get_cluster_objects_by_connected_id(mc_connect_id=connect_id)

    # database error
    if not ok or not cluster_objects:
        error = 'Failed in ClusterDAO.get_cluster_objects_by_connected_id(mc_connect_id=connect_id), ' \
                'mc_connect_id={}, caused by {}'.format(connect_id, error_message)
        logger.error(error)
        raise ValueError(GSLinkManagerError.MULTI_CLUSTER_CONNECTED_REMOTE_CLUSTER_NOT_FOUND.format(cluster=cluster_name))

    # check remote cluster is connected
    connected_cluster_object = None

    # find connected cluster object with cluster_name
    for cluster_object in cluster_objects:
        val = cluster_object.get('cluster_name', None)

        if val and val != cluster_name:
            connected_cluster_object = cluster_object
            break

    # cluster not found for connected cluster
    if not connected_cluster_object:
        raise ValueError(GSLinkManagerError.MULTI_CLUSTER_CONNECTED_REMOTE_CLUSTER_NOT_FOUND.format(cluster=cluster_name))

    connected_cluster_name = connected_cluster_object.get('cluster_name', None)

    # check whether remote cluster is connected or not
    cache = ClusterCache().get_cluster(connected_cluster_name)
    if not cache:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_CONNECTED_ERROR.format(cluster=connected_cluster_name))

    # run export service from agent
    request_id = ClusterAgent.export_service(cluster_id=cluster_name,
                                             namespace=namespace_name,
                                             service=service_name)

    # wait until agent's response arrive(timeout: 60s)
    ok, stdout, stderr = RequestCache().wait(request_id, timeout)
    if not ok:
        if stderr == RequestCache.NOT_READY or stderr == RequestCache.REQUEST_NOT_CACHED:
            error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
            logger.error(error)
            raise SystemError(error)

    do_service_export_view = ServiceViewModel.get_do_service_export_view_model()
    do_service_export_view['name'] = cluster_name
    do_service_export_view['id'] = cluster_id
    do_service_export_view['namespace'] = namespace_name
    do_service_export_view['service'] = service_name
    do_service_export_view['result']['success'] = ok
    do_service_export_view['result']['error'] = stderr
    do_service_export_view['result']['stdout'] = stdout

    return do_service_export_view


def do_unexport_service(cluster_name: str,
                        namespace_name: str,
                        service_name: str,
                        timeout: int = 60) -> dict:
    """
    export service
    :param cluster_name: (str) cluster name
    :param namespace_name: (str) namespace name
    :param service_name: (str) service name
    :param timeout: (int) await seconds
    :return: (dict) service.view_model.do_service_unexport_view_model
    """
    ok, cluster_objects, error_message = ClusterDAO.get_cluster_objects_by_name(cluster_name)

    if not ok or not cluster_objects:
        logger.error(error_message)
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    # check whether request cluster is connected or not
    cache = ClusterCache().get_cluster(cluster_name)
    if not cache:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_CONNECTED_ERROR.format(cluster=cluster_name))

    # check request service is exist or not
    resource = cache['resource']
    services = resource.get_namespace_services_by_service(namespace=namespace_name,
                                                          service=service_name)

    if not services or services[0].get_name() != service_name:
        raise ValueError(GSLinkManagerError.SERVICE_NOT_FOUND_ERROR.format(service=service_name))

    cluster_object = cluster_objects[0]
    cluster_id = cluster_object.get('cluster_id', None)
    connect_id = cluster_object.get('mc_connect_id', None)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    if not connect_id:
        raise ValueError(GSLinkManagerError.NOT_CONNECTED_MC_NETWORK.format(cluster=cluster_name))

    # get all cluster with mc_connect_id
    ok, cluster_objects, error_message = \
        ClusterDAO.get_cluster_objects_by_connected_id(mc_connect_id=connect_id)

    # database error
    if not ok or not cluster_objects:
        error = 'Failed in ClusterDAO.get_cluster_objects_by_connected_id(mc_connect_id=connect_id), ' \
                'mc_connect_id={}, caused by {}'.format(connect_id, error_message)
        logger.error(error)
        raise ValueError(GSLinkManagerError.MULTI_CLUSTER_CONNECTED_REMOTE_CLUSTER_NOT_FOUND.format(cluster=cluster_name))

    # check remote cluster is connected
    connected_cluster_object = None

    # find connected cluster object with cluster_name
    for cluster_object in cluster_objects:
        val = cluster_object.get('cluster_name', None)

        if val and val != cluster_name:
            connected_cluster_object = cluster_object
            break

    # cluster not found for connected cluster
    if not connected_cluster_object:
        raise ValueError(GSLinkManagerError.MULTI_CLUSTER_CONNECTED_REMOTE_CLUSTER_NOT_FOUND.format(cluster=cluster_name))

    connected_cluster_name = connected_cluster_object.get('cluster_name', None)

    # check whether remote cluster is connected or not
    cache = ClusterCache().get_cluster(connected_cluster_name)
    if not cache:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_CONNECTED_ERROR.format(cluster=connected_cluster_name))

    request_id = ClusterAgent.unexport_service(cluster_id=cluster_name,
                                               namespace=namespace_name,
                                               service=service_name)

    # wait until agent's response arrive(timeout: 60s)
    ok, stdout, stderr = RequestCache().wait(request_id, timeout)
    if not ok:
        if stderr in (RequestCache.NOT_READY.value, RequestCache.REQUEST_NOT_CACHED.value):
            error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
            logger.error(error)
            raise SystemError(error)

    # success returns
    do_service_unexport_view = ServiceViewModel.get_do_service_unexport_view_model()
    do_service_unexport_view['name'] = cluster_name
    do_service_unexport_view['id'] = cluster_id
    do_service_unexport_view['namespace'] = namespace_name
    do_service_unexport_view['service'] = service_name
    do_service_unexport_view['result']['success'] = ok
    do_service_unexport_view['result']['error'] = stderr
    do_service_unexport_view['result']['stdout'] = stdout

    return do_service_unexport_view
