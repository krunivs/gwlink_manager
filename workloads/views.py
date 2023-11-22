# Create your views here.
from typing import List
from rest_framework.request import Request
from cache.request_cache import RequestCache
from gwlink_manager import settings
from gwlink_manager.common.error import GSLinkManagerError
from cluster.data_access_object import ClusterDAO
from gwlink_migration.common.type import MigrationStatus
from gwlink_migration.data_access_object import MigrationDAO
from mqtt.api import ClusterAgent
from repository.cache.cluster import ClusterCache
from repository.common.type import ActiveStatus
from repository.model.k8s.condition import Condition
from repository.model.k8s.daemonset import DaemonSet
from repository.model.k8s.deployment import Deployment
from repository.model.k8s.pod import Pod
from utils.dateformat import DateFormatter

from utils.validate import Validator
from workloads.view_model import *

logger = settings.get_logger(__name__)

def get_condition_views(conditions: List[Condition]):
    """
    get condition list view
    :param conditions: (list[repository.model.k8s.condition.Condition])
    :return: (list[workloads.view_model.condition_view_model])
    """
    condition_views = []

    for condition in conditions:
        condition_view = WorkloadViewModel.get_condition_view_model()
        condition_view['condition'] = condition.get_condition()
        condition_view['status'] = condition.get_status()
        condition_view['message'] = condition.get_message()
        condition_view['updated'] = DateFormatter.get_age(condition.get_update())
        condition_views.append(condition_view)

    return condition_views

def get_all_namespace_list() -> dict:
    """
    get all namespace list view
    :return:
    """
    all_namespace_list_view = WorkloadViewModel.get_all_namespace_view_model()

    caches = ClusterCache().get_clusters()

    for key, value in caches.items():
        all_namespace_view = WorkloadViewModel.get_all_namespace_view_model()
        all_namespace_view['name'] = key
        resource = value['resource']
        namespaces = resource.get_namespaces()

        for namespace in namespaces:
            all_namespace_view['namespaces'].append(namespace.get_name())

        all_namespace_view['namespaces'].append('_all_')
        all_namespace_list_view['namespaces'].append(all_namespace_view)

    return all_namespace_list_view


def get_namespace_list_view(cluster_name: str) -> dict:
    """
    get namespace list view
    :param cluster_name: (str) cluster name
    :return: (dict) workloads.view_model.namespace_list_view_model
    """
    namespace_list_view = WorkloadViewModel.get_namespace_list_view_model()
    namespace_list_view['name'] = cluster_name

    if cluster_name is None:
        return namespace_list_view

    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)

    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    namespace_list_view['id'] = cluster_id

    cache = ClusterCache().get_cluster(cluster_name)

    if cache:
        resource = cache['resource']
        namespaces = resource.get_namespaces()

        for namespace in namespaces:
            namespace_view = WorkloadViewModel.get_namespace_view_model()
            namespace_view['name'] = namespace.get_name()
            namespace_view['state'] = namespace.get_state()
            conditions = namespace.get_conditions()
            condition_list_view = get_condition_views(conditions)
            namespace_view['conditions'] = condition_list_view
            namespace_view['stime'] = namespace.get_stime()
            namespace_view['age'] = DateFormatter.get_age(namespace.get_stime())
            namespace_list_view['namespaces'].append(namespace_view)

        # append '_all_' to namespace
        namespace_view = WorkloadViewModel.get_namespace_view_model()
        namespace_view['name'] = '_all_'
        namespace_view['state'] = ActiveStatus.ACTIVE.value
        namespace_view['conditions'] = []
        namespace_view['stime'] = None
        namespace_view['age'] = None
        namespace_list_view['namespaces'].append(namespace_view)

    return namespace_list_view

def delete_namespace(cluster_name: str,
                     namespace_name: str,
                     timeout: int=60) -> dict:
    """
    delete namespace
    :param cluster_name: (str) cluster name
    :param namespace_name: (str) namespace name
    :param timeout: (int) await seconds
    :return: (dict) workload.view_model.pod_deletion_view_model
    :return:
    """
    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)

    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    stdout = None
    stderr = None

    if namespace_name != '_all_':
        # run delete daemonset from agent
        request_id = ClusterAgent.delete_namespace(cluster_id=cluster_name,
                                                   namespace=namespace_name)

        # wait until agent's response arrive(timeout: 60s)
        ok, stdout, stderr = RequestCache().wait(request_id, timeout)
        if not ok:
            if stderr in (RequestCache.NOT_READY.value, RequestCache.REQUEST_NOT_CACHED.value):
                error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
                logger.error(error)
                raise SystemError(error)

    namespace_delete_view = WorkloadViewModel.get_namespace_delete_view_model()
    namespace_delete_view['name'] = cluster_name
    namespace_delete_view['id'] = cluster_id
    namespace_delete_view['namespace'] = namespace_name
    namespace_delete_view['result']['success'] = ok
    namespace_delete_view['result']['stdout'] = stdout
    namespace_delete_view['result']['error'] = stderr

    return namespace_delete_view


def get_pod_views(pods: List[Pod]) -> List[dict]:
    """
    get pod view for Pod
    :param pods: (List[repository.model.k8s.pod.Pod])
    :return:
    """
    pod_views = []

    if not pods or len(pods) <= 0:
        return pod_views

    for pod in pods:
        pod_view = WorkloadViewModel.get_pod_view_model()
        pod_view['name'] = pod.get_name()
        pod_view['state'] = pod.get_state()
        pod_view['namespace'] = pod.get_namespace()
        pod_view['labels'] = pod.get_labels()
        pod_view['host_ip'] = pod.get_host_ip()
        pod_view['node'] = pod.get_node_name()
        pod_view['pod_ip'] = pod.get_pod_ip()
        pod_view['conditions'] = get_condition_views(pod.get_conditions())
        pod_view['images'] = pod.get_images()
        pod_view['stime'] = pod.get_stime()
        pod_view['age'] = DateFormatter.get_age(pod.get_stime())
        pod_views.append(pod_view)

    return pod_views


def get_pod_list_view(cluster_name: str,
                      namespace: str,
                      query_params: dict = None) -> dict:
    """
    get pod list view
    :param cluster_name: (str) cluster name
    :param namespace: (str) namespace name
    :param query_params: (dict)
    :return: (dict) workload.view_model.pod_list_view_model
    """
    # parse query params
    filter_key = None
    filter_value = None
    has_filter = False

    pod_list_view = WorkloadViewModel.get_pod_list_view_model()

    if cluster_name is None:
        return pod_list_view

    pod_list_view['name'] = cluster_name

    if query_params is not None and len(query_params.keys()) > 0:
        if len(query_params.keys()) != 1:
            raise KeyError('Query parameter should must be only one of the [service, deployment, daemonset]')
        if 'service' in query_params.keys():
            filter_key = 'service'
            filter_value = query_params['service']
            has_filter = True
        elif 'deployment' in query_params.keys():
            filter_key = 'deployment'
            filter_value = query_params['deployment']
            has_filter = True
        elif 'daemonset' in query_params.keys():
            filter_key = 'daemonset'
            filter_value = query_params['daemonset']
            has_filter = True
        else:
            error = 'Query parameter should must be only one of the ' \
                    '[service, deployment, daemonset]'
            logger.error(error)
            raise KeyError(error)

    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)
    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    if namespace is None:
        return pod_list_view

    pod_list_view['name'] = cluster_name
    pod_list_view['id'] = cluster_id

    cache = ClusterCache().get_cluster(cluster_name)

    if cache:
        resource = cache['resource']
        if has_filter: # filtered by service, daemonset, deployment
            if filter_key == 'service':
                if namespace == '_all_':
                    pods = resource.get_all_namespace_pods_by_service(filter_value)
                else:
                    pods = resource.get_namespace_pods_by_service(namespace, filter_value)
            elif filter_key == 'deployment':
                if namespace == '_all_':
                    pods = resource.get_all_namespace_pods_by_deployment(filter_value)
                else:
                    pods = resource.get_namespace_pods_by_deployment(namespace, filter_value)
            elif filter_key == 'daemonset': # 'daemonset'
                if namespace == '_all_':
                    pods = resource.get_all_namespace_pods_by_daemonset(filter_value)
                else:
                    pods = resource.get_namespace_pods_by_daemonset(namespace, filter_value)
            else:
                raise ValueError(GSLinkManagerError.BAD_REQUEST_ERROR)
        else:
            if namespace == '_all_':
                pods = resource.get_all_namespace_pods()
            else:
                pods = resource.get_namespace_pods(namespace)

        pod_list_view['pods'] = get_pod_views(pods)

    return pod_list_view


def get_pod_view(cluster_name: str,
                 namespace: str,
                 pod_name: str) -> dict:
    """
    get pod view
    :param cluster_name: (str) cluster name
    :param namespace: (str) namespace name
    :param pod_name: (str) pod name
    :return: (dict) workload.view_model.pod_list_view_model
    """
    pod_list_view = WorkloadViewModel.get_pod_list_view_model()

    if cluster_name is None:
        return pod_list_view

    pod_list_view['name'] = cluster_name

    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)

    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    pod_list_view['id'] = cluster_id

    if namespace is None or pod_name is None:
        return pod_list_view

    cache = ClusterCache().get_cluster(cluster_name)

    if cache:
        resource = cache['resource']

        if namespace == '_all_':
            pods = resource.get_all_namespace_pods_by_pod(pod_name)
        else:
            pods = resource.get_namespace_pods_by_pod(namespace, pod_name)

        pod_list_view['pods'] = get_pod_views(pods)

    return pod_list_view

def delete_pod(cluster_name: str,
               namespace_name: str,
               pod_name: str,
               timeout: int=60) -> dict:
    """
    delete pod
    :param cluster_name: (str) cluster name
    :param namespace_name: (str) namespace name
    :param pod_name: (str) pod name
    :param timeout: (int) await seconds
    :return: (dict) workload.view_model.pod_deletion_view_model
    """
    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)
    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    # run delete pod from agent
    request_id = ClusterAgent.delete_pod(cluster_id=cluster_name,
                                         namespace=namespace_name,
                                         pod=pod_name)

    # wait until agent's response arrive(default timeout: 60s)
    ok, stdout, stderr = RequestCache().wait(request_id, timeout)
    if not ok:
        if stderr == RequestCache.NOT_READY or stderr == RequestCache.REQUEST_NOT_CACHED:
            error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
            logger.error(error)
            raise SystemError(error)

    pod_deletion_view = WorkloadViewModel.get_pod_deletion_view_model()
    pod_deletion_view['name'] = cluster_name
    pod_deletion_view['id'] = cluster_id
    pod_deletion_view['pod'] = pod_name
    pod_deletion_view['namespace'] = namespace_name
    pod_deletion_view['result']['success'] = ok
    pod_deletion_view['result']['stdout'] = stdout
    pod_deletion_view['result']['error'] = stderr

    return pod_deletion_view


def get_pod_migratable_cluster_list_view(cluster_name: str,
                                         namespace: str,
                                         pod: str) -> dict:
    """
    get pod migratable cluster list view
    :param cluster_name: (str) cluster name
    :param namespace: (str) cluster namespace
    :param pod: (str) pod name
    :return:
    """
    # get cluster object for selected cluster_name
    ok, cluster_objects, error_message = ClusterDAO.get_cluster_objects_by_name(cluster_name)

    """ get cluster DB entry for request cluster_name """
    if not ok or not cluster_objects:
        error = 'Failed in ClusterDAO.get_cluster_objects_by_name({}}), ' \
                'caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    # selected cluster object
    selected_cluster_object = cluster_objects[0]
    selected_cluster_name = selected_cluster_object.get('cluster_name', None)
    selected_cluster_id = selected_cluster_object.get('cluster_id', None)
    connect_id = selected_cluster_object.get('mc_connect_id', None)

    """ get cluster DB entry for target cluster connected """
    ok, cluster_objects, error_message = \
        ClusterDAO.get_cluster_objects_by_connected_id(mc_connect_id=connect_id)

    if not ok or not cluster_objects:
        error = 'Failed in ClusterDAO.get_cluster_objects_by_connected_id({}}), ' \
                'caused by {}'.format(connect_id, error_message)
        logger.error(error)
        raise ValueError(GSLinkManagerError.MULTI_CLUSTER_CONNECTED_REMOTE_CLUSTER_NOT_FOUND.format(cluster=cluster_name))

    # target cluster object
    target_cluster_object = None

    for item in cluster_objects:
        temp_cluster_id = item.get('cluster_id', None)
        if selected_cluster_id != temp_cluster_id:
            target_cluster_object = item
            break

    if not target_cluster_object:
        error = 'Not found target cluster in database'
        logger.error(error)
        raise ValueError(GSLinkManagerError.MULTI_CLUSTER_CONNECTED_REMOTE_CLUSTER_NOT_FOUND.format(cluster=cluster_name))

    target_cluster_id = target_cluster_object.get('cluster_id', None)
    target_cluster_name = target_cluster_object.get('cluster_name', None)

    # check whether request pod is exist in selected cluster
    selected_cluster_cache = ClusterCache().get_cluster(selected_cluster_name)

    """ validate request pod """
    if not selected_cluster_cache:
        error = 'Not found request cluster name({}) in cluster cache'.format(cluster_name)
        logger.error(error)
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_CONNECTED_ERROR.format(cluster=cluster_name))

    # cache.resources.ResourceCache
    selected_cluster_cache_resource = selected_cluster_cache['resource']

    # repository.model.k8s.pod.Pod
    pods = selected_cluster_cache_resource.get_pods()
    if not pods:
        error = 'Failed in selected_cluster_cache_resource.get_pods(), caused by No pod entry in cache'
        logger.error(error)
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_CONNECTED_ERROR.format(cluster=cluster_name))

    ok = False
    for item in pods:
        pod_name = item.get_name()
        pod_namespace = item.get_namespace()

        if pod_name == pod and pod_namespace == namespace:
            ok = True
            break

    if not ok:
        error = 'Not found pod({}), namespace({}) in cluster({})'.format(pod, namespace, cluster_name)
        logger.error(error)
        raise ValueError(GSLinkManagerError.POD_NOT_FOUND_ERROR.format(cluster=cluster_name, pod=pod, namespace=namespace))

    """ retrieve target cluster node list to get candidate migrate node """
    target_cluster_cache = ClusterCache().get_cluster(target_cluster_name)
    if not target_cluster_cache:
        error = 'Not found target cluster name({}) in cluster cache'.format(target_cluster_name)
        logger.error(error)
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_CONNECTED_ERROR.format(cluster=target_cluster_name))

    # cache.resources.ResourceCache
    target_cluster_cache_resource =  target_cluster_cache['resource']

    # repository.model.k8s.node.Node
    nodes = target_cluster_cache_resource.get_nodes()
    if not nodes:
        error = 'Failed in target_cluster_cache_resource.get_nodes(), caused by No node entry in cache'
        logger.error(error)
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_CONNECTED_ERROR.format(cluster=cluster_name))

    pod_migratable_cluster_list_view = WorkloadViewModel.get_pod_migratable_cluster_list_view_model()
    pod_migratable_cluster_list_view['name'] = selected_cluster_name
    pod_migratable_cluster_list_view['id'] = selected_cluster_id

    migratable_cluster_view = WorkloadViewModel.get_pod_migratable_cluster_view_model()
    migratable_cluster_view['name'] = target_cluster_name
    migratable_cluster_view['id'] = target_cluster_id

    for item in nodes:
        # DO NOT assign to master node
        if item.get_role() != 'Master':
            migratable_cluster_view['nodes'].append(item.get_name())

    pod_migratable_cluster_list_view['clusters'].append(migratable_cluster_view)

    return pod_migratable_cluster_list_view


def do_pod_migration(request: Request,
                     cluster_name: str,
                     namespace: str,
                     pod: str,
                     timeout: int=60) -> dict:
    """
    do pod migration
    :param request: (rest_framework.request.Request)
    :param cluster_name: (str) cluster name
    :param namespace: (str) namespace name
    :param pod: (str) pod name
    :param timeout: (int) timeout
    :return:
    """
    # check request body
    if 'target_cluster' not in request.data:
        raise KeyError(GSLinkManagerError.BODY_FIELD_NOT_FOUND_ERROR.format(field='target.cluster'))

    if 'target_node' not in request.data:
        raise KeyError(GSLinkManagerError.BODY_FIELD_NOT_FOUND_ERROR.format(field='target.node'))

    if 'delete_origin' not in request.data:
        delete_origin = False  # default

    else:
        if not Validator.is_enable_cast_to_bool(request.data['delete_origin']):
            raise ValueError(GSLinkManagerError.INVALID_BODY_FIELD_VALUE.format(field='delete_origin',
                                                                                val=request.data['delete_origin']))
        delete_origin = Validator.cast_to_bool(request.data['delete_origin'])

    target_cluster_name = request.data['target_cluster']

    """ validate request cluster name """
    ok, cluster_objects, error_message = ClusterDAO.get_cluster_objects_by_name(cluster_name)

    if not ok or not cluster_objects:
        error = 'Failed in ClusterDAO.get_cluster_objects_by_name({}}), ' \
                'caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    selected_cluster_object = cluster_objects[0]
    selected_cluster_connect_id = selected_cluster_object.get('mc_connect_id', None)

    if not selected_cluster_connect_id:
        error = 'Not found multi-cluster connect id for cluster({}})'.format(cluster_name)
        logger.error(error)
        raise ValueError(GSLinkManagerError.NOT_CONNECTED_MC_NETWORK.format(cluster=cluster_name))

    """ validate target cluster name """
    ok, cluster_objects, error_message = ClusterDAO.get_cluster_objects_by_name(target_cluster_name)

    if not ok or not cluster_objects:
        error = 'Failed in ClusterDAO.get_cluster_objects_by_name({}}), ' \
                'caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=target_cluster_name))

    target_cluster_object = cluster_objects[0]
    target_cluster_id = target_cluster_object.get('cluster_id', None)
    target_cluster_connect_id = target_cluster_object.get('mc_connect_id')

    if not target_cluster_connect_id:
        error = 'Not found multi-cluster connect id for cluster({}})'.format(target_cluster_name)
        logger.error(error)
        raise ValueError(GSLinkManagerError.NOT_CONNECTED_MC_NETWORK.format(cluster=target_cluster_name))

    """ validate multi-cluster network configuration """
    if selected_cluster_connect_id != target_cluster_connect_id:
        error = 'Invalid multi-cluster connection between cluster({}), cluster({})'.format(
            cluster_name, target_cluster_name)
        logger.error(error)
        raise ValueError(GSLinkManagerError.INVALID_MULTI_CLUSTER_NETWORK.format(
            cluster1=cluster_name, cluster2=target_cluster_name))

    selected_cluster_name = selected_cluster_object.get('cluster_name', None)
    selected_cluster_id = selected_cluster_object.get('cluster_id', None)
    selected_cluster_role = selected_cluster_object.get('role', None)
    target_cluster_node = request.data['target_node']

    """ validate migration request pod, namespace """
    cache = ClusterCache().get_cluster(selected_cluster_name)

    if not cache:
        error = 'Not found request cluster({}) in cache'.format(selected_cluster_name)
        logger.error(error)
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=selected_cluster_name))

    # resource: ResourceCache()
    resource = cache['resource']
    found = False

    # pod_list: List[Pod]
    pod_list = resource.get_namespace_pods(namespace)
    for item in pod_list:
        if pod == item.get_name():
            found = True
            break

    if not found:
        error = 'Not found request pod({}) in cache'.format(pod)
        logger.error(error)
        raise ValueError(GSLinkManagerError.POD_NOT_FOUND_ERROR.format(cluster=selected_cluster_name,
                                                                       namespace=namespace,
                                                                       pod=pod))

    """ validate target node """
    cache = ClusterCache().get_cluster(target_cluster_name)

    if not cache:
        error = 'Not found target cluster({}) in cache'.format(target_cluster_name)
        logger.error(error)
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster_name=target_cluster_name))

    # resource: ResourceCache()
    resource = cache['resource']
    found = False

    # node_list: List[Node]
    node_list = resource.get_nodes()
    for item in node_list:
        if item.get_name() == target_cluster_node:
            found = True

    if not found:
        error = 'Not found target node({}) in cache'.format(target_cluster_node)
        logger.error(error)
        raise ValueError(GSLinkManagerError.NODE_NOT_FOUND_ERROR.format(cluster=target_cluster_name,
                                                                        node=target_cluster_node))

    """ scheduled to migrate pod from selected to target """
    # check duplication for migration request
    ok, migration_requests, error_message = \
        MigrationDAO.find_migration_requests(source_cluster_name=selected_cluster_name,
                                             source_namespace=namespace,
                                             source_pod=pod,
                                             target_cluster_name=target_cluster_name,
                                             target_node_name=target_cluster_node)

    if not ok:
        error = 'Failed in MigrationDAO.find_migration_request(), caused by ' + error_message
        logger.error(error)
        raise SystemError(error)

    if len(migration_requests) > 0:
        # if previous request is completed with error, delete it and set new request
        # otherwise, return error
        status = migration_requests[0].status

        if status in (MigrationStatus.RUNNING.value,
                      MigrationStatus.PENDING.value,
                      MigrationStatus.ISSUED.value):
            error = GSLinkManagerError.MIGRATION_ALREADY_EXIST.format(
                cluster1=selected_cluster_name,
                cluster2=target_cluster_name,
                node=target_cluster_node,
                pod=pod,
                namespace=namespace)
            logger.error(error)

            raise ValueError(error)

    # create migration
    ok, error_message = MigrationDAO.create_migration(source_cluster_name=selected_cluster_name,
                                                      source_cluster_role=selected_cluster_role,
                                                      source_namespace=namespace,
                                                      source_pod=pod,
                                                      target_cluster_name=target_cluster_name,
                                                      target_node_name=target_cluster_node,
                                                      delete_origin=delete_origin)
    if not ok:
        error = 'Failed in MigrationDAO.set_migration(), caused by ' + error_message
        logger.error(error)
        raise SystemError(error)

    """ pack response view model """
    do_pod_migrate_view = WorkloadViewModel.get_do_pod_migrate_view_model()
    do_pod_migrate_view['name'] = selected_cluster_name
    do_pod_migrate_view['id'] = selected_cluster_id
    do_pod_migrate_view['namespace'] = namespace
    do_pod_migrate_view['pod'] = pod
    do_pod_migrate_view['namespace'] = namespace
    do_pod_migrate_view['target']['cluster'] = target_cluster_name
    do_pod_migrate_view['target']['id'] = target_cluster_id
    do_pod_migrate_view['target']['node'] = target_cluster_node
    do_pod_migrate_view['stime'] = DateFormatter.current_datetime_app_format()

    return do_pod_migrate_view


def get_pod_migration_log_list_view(cluster: str,
                                    timeout: int = 60) -> dict:
    """
    delete pod migration log list
    :param cluster: (str) source cluster name
    :param timeout: (int) timeout
    :return:
    """
    ok, cluster_objects, error_message = ClusterDAO.get_cluster_objects_by_name(cluster)

    if not ok or not cluster_objects:
        error = 'Failed in ClusterDAO.get_cluster_objects_by_name({}}), ' \
                'caused by {}'.format(cluster, error_message)
        logger.error(error)
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster))

    cluster_migration_log_list_view = WorkloadViewModel.get_cluster_migration_log_list_view()
    cluster_migration_log_list_view['name'] = cluster
    cluster_migration_log_list_view['id'] = cluster_objects[0].get('cluster_id', None)

    # iterate MigrationRequest and MigrationTask table
    ok, request_objects, error = MigrationDAO.get_migration_requests()

    if not ok:  # error return
        error = 'Failed in MigrationDAO.get_migration_requests({}}), ' \
                'caused by {}'.format(cluster, error)
        logger.error(error)

        return SystemError(error)

    for request_object in request_objects:
        cluster_migration_log_view = WorkloadViewModel.get_cluster_migration_log_view()
        last_subtask_seq = request_object.last_subtask_seq
        status = request_object.status
        start_date = request_object.start_date
        end_date = request_object.end_date

        if start_date:
            start_date = start_date.split('.')[0]
        if end_date:
            end_date = end_date.split('.')[0]

        # fill migration log
        source_cluster = request_object.source_cluster_name
        target_cluster = request_object.target_cluster_name

        if source_cluster != cluster and target_cluster != cluster:
            continue

        cluster_migration_log_view['migration_id'] = request_object.id
        cluster_migration_log_view['source_cluster'] = source_cluster
        cluster_migration_log_view['source_namespace'] = request_object.source_namespace
        cluster_migration_log_view['source_pod'] = request_object.source_pod
        cluster_migration_log_view['target_cluster'] = target_cluster
        cluster_migration_log_view['target_node'] = request_object.target_node_name
        cluster_migration_log_view['state'] = status
        cluster_migration_log_view['start_date'] = start_date
        cluster_migration_log_view['end_date'] = end_date

        if status in MigrationStatus.COMPLETED.value:
            cluster_migration_log_view['task'] = ''
            cluster_migration_log_view['retry'] = 0
            cluster_migration_log_view['error'] = ''
        else:
            ok, subtask_objects, error = \
                MigrationDAO.get_migration_subtask_by_sequence(request_object, last_subtask_seq)

            if not ok:  # error return
                error_message = 'Failed in MigrationDAO.get_migration_subtask_by_sequence({}, {}), ' \
                                'caused by Not found subtask'.format(request_object, last_subtask_seq)
                logger.error(error_message)

                continue

            if not subtask_objects:
                error_message = 'Failed in MigrationDAO.get_migration_subtask_by_sequence({}, {}), ' \
                                'caused by Not found subtask'.format(request_object, last_subtask_seq)
                logger.error(error_message)

                continue

            subtask_object = subtask_objects[0]
            cluster_migration_log_view['task'] = subtask_object.task
            cluster_migration_log_view['retry'] = subtask_object.retry
            cluster_migration_log_view['error'] = subtask_object.reason

        cluster_migration_log_list_view['logs'].append(cluster_migration_log_view)

    return cluster_migration_log_list_view


def delete_pod_migration_log(cluster: str, migration_id: str) -> dict:
    """
    delete pod migration log
    :param cluster: (str) cluster name
    :param migration_id: (str) migration UUID
    :return:
    """
    ok, cluster_objects, error_message = ClusterDAO.get_cluster_objects_by_name(cluster)

    if not ok or not cluster_objects:
        error = 'Failed in ClusterDAO.get_cluster_objects_by_name({}}), ' \
                'caused by {}'.format(cluster, error_message)
        logger.error(error)
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster))

    ok, migration_object, error = MigrationDAO.get_migration_request(migration_id)

    if not ok:
        raise ValueError(GSLinkManagerError.MIGRATION_NOT_EXIST.format(migration_id=migration_id))
    #
    # if migration_object.status in (MigrationStatus.ISSUED.value,
    #                                MigrationStatus.RUNNING.value,
    #                                MigrationStatus.PENDING.value):
    #     raise ValueError(GSLinkManagerError.MIGRATION_IN_PROGRESS.format(migration_id=migration_id))

    delete_pod_migration_log_view = WorkloadViewModel.get_delete_pod_migration_log_view()
    delete_pod_migration_log_view['name'] = cluster
    delete_pod_migration_log_view['id'] = cluster_objects[0].get('cluster_id', None)

    # delete pod migration log
    ok, error = MigrationDAO.delete_migration(migration_id)

    if not ok:
        delete_pod_migration_log_view['result']['success'] = False
        delete_pod_migration_log_view['result']['error'] = error
    else:
        delete_pod_migration_log_view['result']['success'] = True
        delete_pod_migration_log_view['result']['error'] = None

    return delete_pod_migration_log_view


def get_deployment_views(deployments: List[Deployment]) -> List[dict]:
    """
    get deployment view for Deployment list
    :param deployments: (List[repository.model.k8s.deployment.Deployment])
    :return:
    """
    deployment_views = []

    if not deployments or len(deployments) <= 0:
        return deployment_views

    for deployment in deployments:
        deployment_view = WorkloadViewModel.get_deployment_view_model()
        deployment_view['name'] = deployment.get_name()
        deployment_view['state'] = deployment.get_state()
        deployment_view['namespace'] = deployment.get_namespace()
        deployment_view['images'] = deployment.get_images()
        deployment_view['ready_replicas'] = deployment.get_ready_replicas()
        deployment_view['replicas'] = deployment.get_replicas()
        deployment_view['restart'] = deployment.get_restart()
        deployment_view['selector'] = deployment.get_selector()
        deployment_view['conditions'] = get_condition_views(deployment.get_conditions())
        deployment_view['stime'] = deployment.get_stime()
        deployment_view['age'] = DateFormatter.get_age(deployment.get_stime())

        deployment_views.append(deployment_view)

    return deployment_views


def get_deployment_list_view(cluster_name: str,
                             namespace: str,
                             query_params: dict = None) -> dict:
    """
    get deployment list view
    :param cluster_name: (str) cluster name
    :param namespace: (str) namespace name
    :param query_params: (dict)
    :return: (dict) workload.view_model.deployment_list_view_model
    """
    # parse query params
    filter_key = None
    filter_value = None
    has_filter = False

    deployment_list_view = WorkloadViewModel.get_deployment_list_view_model()

    if cluster_name is None:
        return deployment_list_view

    deployment_list_view['name'] = cluster_name

    if namespace is None:
        return deployment_list_view

    if query_params is not None and len(query_params.keys()) > 0:
        if len(query_params.keys()) != 1:
            raise KeyError('Query parameter should must be only one of the [pod]')
        if 'pod' in query_params.keys():
            filter_key = 'pod'
            filter_value = query_params['pod']
            has_filter = True
        else:
            raise KeyError('Query parameter should must be only one of the [pod]')

    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)
    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    deployment_list_view['id'] = cluster_id

    if namespace is None:
        return deployment_list_view

    cache = ClusterCache().get_cluster(cluster_name)

    if cache:
        resource = cache['resource']
        if has_filter: # filtered by pod
            if filter_key == 'pod':
                if namespace == '_all_':
                    deployments = resource.get_all_namespace_deployments_by_pod(filter_value)
                else:
                    deployments = resource.get_namespace_deployments_by_pod(namespace, filter_value)
            else:
                error = 'Invalid filter option. Only support one of the [pod]'
                logger.error(error)
                raise SystemError(error)
        else:
            if namespace == '_all_':
                deployments = resource.get_all_namespace_deployments()
            else:
                deployments = resource.get_namespace_deployments(namespace)

        deployment_list_view['deployments'] = get_deployment_views(deployments)

    return deployment_list_view


def get_deployment_view(cluster_name: str,
                        namespace: str,
                        deployment_name: str) -> dict:
    """
    get deployment view
    :param cluster_name: (str) cluster name
    :param namespace: (str) namespace name
    :param deployment_name: (str) deployment name
    :return: (dict) workload.view_model.deployment_list_view_model
    """
    deployment_list_view = WorkloadViewModel.get_deployment_list_view_model()

    if cluster_name is None:
        return deployment_list_view

    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)

    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    deployment_list_view['name'] = cluster_name
    deployment_list_view['id'] = cluster_id

    if namespace is None or deployment_name is None:
        return deployment_list_view

    cache = ClusterCache().get_cluster(cluster_name)

    if cache:
        resource = cache['resource']

        if namespace == '_all_':
            deployments = resource.get_all_namespace_deployments_by_deployment(deployment_name)
        else:
            deployments = resource.get_namespace_deployments_by_deployment(namespace, deployment_name)

        deployment_list_view['deployments'] = get_deployment_views(deployments)

    return deployment_list_view

def delete_deployment(cluster_name: str,
                      namespace_name: str,
                      deployment_name: str,
                      timeout: int=60) -> dict:
    """
    delete deployment
    :param cluster_name: (str) cluster name
    :param namespace_name: (str) namespace name
    :param deployment_name:  (str) deployment name
    :param timeout:  (int) await timeout
    :return: workload.view_model.deployment_deletion_view_model
    """
    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)

    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    # run delete deployment from agent
    request_id = ClusterAgent.delete_deployment(cluster_id=cluster_name,
                                                namespace=namespace_name,
                                                deployment=deployment_name)

    # wait until agent's response arrive(timeout: 60s)
    ok, stdout, stderr = RequestCache().wait(request_id, timeout)
    if not ok:
        if stderr == RequestCache.NOT_READY or stderr == RequestCache.REQUEST_NOT_CACHED:
            error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
            logger.error(error)
            raise SystemError(error)

    deployment_deletion_view = WorkloadViewModel.get_deployment_deletion_view_model()
    deployment_deletion_view['name'] = cluster_name
    deployment_deletion_view['id'] = cluster_id
    deployment_deletion_view['namespace'] = namespace_name
    deployment_deletion_view['deployment'] = deployment_name
    deployment_deletion_view['result']['success'] = ok
    deployment_deletion_view['result']['stdout'] = stdout
    deployment_deletion_view['result']['error'] = stderr

    return deployment_deletion_view


def get_daemonset_views(daemonsets: List[DaemonSet]) -> List[dict]:
    """
    get daemonset view for DaemonSet list
    :param daemonsets: (List[repository.model.k8s.daemonset.DaemonSet])
    :return:
    """
    daemonset_views = []

    if not daemonsets or len(daemonsets) <= 0:
        return daemonset_views

    for daemonset in daemonsets:
        daemonset_view = WorkloadViewModel.get_daemonset_view_model()
        daemonset_view['name'] = daemonset.get_name()
        daemonset_view['state'] = daemonset.get_state()
        daemonset_view['namespace'] = daemonset.get_namespace()
        daemonset_view['images'] = daemonset.get_images()
        daemonset_view['desired'] = daemonset.get_desired()
        daemonset_view['current'] = daemonset.get_current()
        daemonset_view['ready'] = daemonset.get_ready()
        daemonset_view['selector'] = daemonset.get_selector()
        daemonset_view['conditions'] = get_condition_views(daemonset.get_conditions())
        daemonset_view['age'] = DateFormatter.get_age(daemonset.get_stime())
        daemonset_views.append(daemonset_view)

    return daemonset_views


def get_daemonset_list_view(cluster_name: str,
                            namespace: str,
                            query_params: dict = None) -> dict:
    """
    get daemonset list view
    :param cluster_name: (str) cluster name
    :param namespace: (str) namespace name
    :param query_params: (dict)
    :return: (dict) workload.view_model.daemonset_list_view_model
    """
    # parse query params
    filter_key = None
    filter_value = None
    has_filter = False

    daemonset_list_view = WorkloadViewModel.get_daemonset_list_view_model()

    if cluster_name is None:
        return daemonset_list_view

    daemonset_list_view['name'] = cluster_name

    if query_params is not None and len(query_params.keys()) > 0:
        if len(query_params.keys()) != 1:
            raise KeyError('Query parameter should must be only one of the [pod]')
        if 'pod' in query_params.keys():
            filter_key = 'pod'
            filter_value = query_params['pod']
            has_filter = True
        else:
            raise KeyError('Query parameter should must be only one of the [pod]')

    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)
    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    daemonset_list_view['id'] = cluster_id

    if namespace is None:
        return daemonset_list_view

    cache = ClusterCache().get_cluster(cluster_name)

    if cache:
        resource = cache['resource']
        if has_filter: # filtered by pod
            if filter_key == 'pod':
                if namespace == '_all_':
                    daemonsets = resource.get_all_namespace_daemonsets_by_pod(filter_value)
                else:
                    daemonsets = resource.get_namespace_daemonsets_by_pod(namespace, filter_value)
            else:
                error = 'Invalid filter option. Only support one of the [pod]'
                logger.error(error)
                raise SystemError(error)
        else:
            if namespace == '_all_':
                daemonsets = resource.get_all_namespace_daemonsets()
            else:
                daemonsets = resource.get_namespace_daemonsets(namespace)

        daemonset_list_view['daemonsets'] = get_daemonset_views(daemonsets)

    return daemonset_list_view


def get_daemonset_view(cluster_name: str,
                       namespace: str,
                       daemonset_name: str) -> dict:
    """
    get daemonset view
    :param cluster_name: (str) cluster name
    :param namespace: (str) namespace name
    :param daemonset_name: (str) daemonset name
    :return: (dict) workload.view_model.daemonset_list_view_model
    """
    daemonset_list_view = WorkloadViewModel.get_daemonset_list_view_model()

    if cluster_name is None:
        return daemonset_list_view

    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)

    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    daemonset_list_view['name'] = cluster_name
    daemonset_list_view['id'] = cluster_id

    if namespace is None or daemonset_name is None:
        return daemonset_list_view

    cache = ClusterCache().get_cluster(cluster_name)

    if cache:
        resource = cache['resource']

        if namespace == '_all_':
            daemonsets = resource.get_all_namespace_daemonsets_by_daemonset(daemonset_name)
        else:
            daemonsets = resource.get_namespace_daemonsets_by_daemonset(namespace, daemonset_name)

        daemonset_list_view['daemonsets'] = get_daemonset_views(daemonsets)

    return daemonset_list_view


def delete_daemonset(cluster_name: str,
                     namespace_name: str,
                     daemonset_name: str,
                     timeout: int=60) -> dict:
    """
    delete deployment
    :param cluster_name: (str) cluster name
    :param namespace_name: (str) namespace name
    :param daemonset_name:  (str) daemonset name
    :param timeout:  (int) await timeout
    :return: workload.view_model.daemonset_deletion_view_model
    """
    ok, cluster_id, error_message = ClusterDAO.get_cluster_id(cluster_name)
    if not ok:
        error = 'Not found cluster({}) entry in database, caused by {}'.format(cluster_name, error_message)
        logger.error(error)
        raise SystemError(error)

    if not cluster_id:
        raise ValueError(GSLinkManagerError.CLUSTER_NOT_FOUND_ERROR.format(cluster=cluster_name))

    # run delete daemonset from agent
    request_id = ClusterAgent.delete_daemonset(cluster_id=cluster_name,
                                                namespace=namespace_name,
                                                daemonset=daemonset_name)

    # wait until agent's response arrive(timeout: 60s)
    ok, stdout, stderr = RequestCache().wait(request_id, timeout)
    if not ok:
        if stderr == RequestCache.NOT_READY or stderr == RequestCache.REQUEST_NOT_CACHED:
            error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
            logger.error(error)
            raise SystemError(error)

    daemonset_deletion_view = WorkloadViewModel.get_daemonset_deletion_view_model()
    daemonset_deletion_view['name'] = cluster_name
    daemonset_deletion_view['id'] = cluster_id
    daemonset_deletion_view['namespace'] = namespace_name
    daemonset_deletion_view['daemonset'] = daemonset_name
    daemonset_deletion_view['result']['success'] = ok
    daemonset_deletion_view['result']['stdout'] = stdout
    daemonset_deletion_view['result']['error'] = stderr

    return daemonset_deletion_view
