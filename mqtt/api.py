import os

from cache.request_cache import RequestCache
from mqtt.model.common.type import Method, ContentType
from mqtt.model.content import Content
from mqtt.model.file_content import FileContent
from mqtt.model.request import Request
from mqtt.producer import Publisher
from repository.common.type import MultiClusterRole
from utils.dateformat import DateFormatter


class ClusterAgent:
    """
    CEdge-agent requests
    """
    @staticmethod
    def get_request(path: str) -> Request:
        """
        'GET' request
        :param path: (str) request url path
        :return: (mqtt.model.request.Request)
        """
        request = Request()
        request_id = RequestCache().issue_request_id()
        request.set_request_id(request_id)
        request.set_method(Method.GET.value)
        request.set_path(path)
        request.set_body('')
        request.set_create_date(DateFormatter.current_datetime())

        return request

    @staticmethod
    def post_request(path: str, body: dict) -> Request:
        """
        'POST' request
        :param path: (str) request url path
        :param body: (dict) request body; Nullable
        :return: (mqtt.model.request.Request)
        """
        if not type(body):
            if type(body) != dict:
                raise TypeError('Invalid type for body. Must be dict')

        # create request cache
        request = Request()
        request_id = RequestCache().issue_request_id()
        request.set_request_id(request_id)
        request.set_method(Method.POST.value)
        request.set_path(path)
        request.set_body(body)
        request.set_create_date(DateFormatter.current_datetime())

        return request

    @staticmethod
    def delete_request(path: str) -> Request:
        """
        'DELETE' request
        :param path: (str) request url path
        :return: (mqtt.model.request.Request)
        """
        # create Request instance
        request = Request()
        request_id = RequestCache().issue_request_id()
        request.set_request_id(request_id)
        request.set_method(Method.DELETE.value)
        request.set_path(path)
        request.set_body('')
        request.set_create_date(DateFormatter.current_datetime())

        return request

    @staticmethod
    def put_request(path: str, body: dict) -> Request:
        """
        'PUT' request
        :param path: (str) request url path
        :param body: (dict) request body; Nullable
        :return: (mqtt.model.request.Request)
        """
        if not type(body):
            if type(body) != dict:
                raise TypeError('Invalid type for body. Must be dict')

        # create Request instance
        request = Request()
        request_id = RequestCache().issue_request_id()
        request.set_request_id(request_id)
        request.set_method(Method.PUT.value)
        request.set_path(path)
        request.set_body(body)
        request.set_create_date(DateFormatter.current_datetime())

        return request

    @staticmethod
    def delete_namespace(cluster_id: str, namespace: str) -> str:
        """
        delete namespace
        :param cluster_id: (str)
        :param namespace: (str)
        :return:  (str) request_id
        """
        if type(cluster_id) != str:
            raise TypeError('Invalid type for cluster_id')
        if type(namespace) != str:
            raise TypeError('Invalid type for namespace')

        # create request
        path = '/cluster/{cluster}/namespace/{namespace}'.format(cluster=cluster_id,
                                                                 namespace=namespace)
        request = ClusterAgent.delete_request(path)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def delete_pod(cluster_id: str, namespace: str, pod: str) -> str:
        """
        delete pod
        :param cluster_id: (str) cluster name
        :param namespace: (str) namespace name
        :param pod: (str) pod name
        :return: (str) request_id
        """
        if type(cluster_id) != str:
            raise TypeError('Invalid type for cluster_id')
        if type(namespace) != str:
            raise TypeError('Invalid type for namespace')
        if type(pod) != str:
            raise TypeError('Invalid type for pod')

        # create request
        path = '/cluster/{cluster}/namespace/{namespace}/pod/{pod}'.format(cluster=cluster_id,
                                                                           namespace=namespace,
                                                                           pod=pod)
        request = ClusterAgent.delete_request(path)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def delete_service(cluster_id: str, namespace: str, service: str) -> str:
        """
        delete service
        :param cluster_id: (str) cluster name
        :param namespace: (str) namespace name
        :param service: (str) service name
        :return: (str) request_id
        """
        if type(cluster_id) != str:
            raise TypeError('Invalid type for cluster_id')
        if type(namespace) != str:
            raise TypeError('Invalid type for namespace')
        if type(service) != str:
            raise TypeError('Invalid type for service')

        # create request
        path = '/cluster/{cluster}/namespace/{namespace}/service/{service}'.format(cluster=cluster_id,
                                                                                   namespace=namespace,
                                                                                   service=service)
        request = ClusterAgent.delete_request(path)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def delete_deployment(cluster_id: str, namespace: str, deployment: str) -> str:
        """
        delete deployment
        :param cluster_id: (str) cluster name
        :param namespace: (str) namespace name
        :param deployment: (str) deployment name
        :return: (str) request_id
        """
        if type(cluster_id) != str:
            raise TypeError('Invalid type for cluster_id')
        if type(namespace) != str:
            raise TypeError('Invalid type for namespace')
        if type(deployment) != str:
            raise TypeError('Invalid type for deployment')

        # create request
        path = '/cluster/{cluster}/namespace/{namespace}/deployment/{deployment}'.format(cluster=cluster_id,
                                                                                         namespace=namespace,
                                                                                         deployment=deployment)
        request = ClusterAgent.delete_request(path)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def delete_daemonset(cluster_id: str, namespace: str, daemonset: str) -> str:
        """
        delete daemonset
        :param cluster_id: (str) cluster name
        :param namespace: (str) namespace name
        :param daemonset: (str) daemonset name
        :return: (str) request_id
        """
        if type(cluster_id) != str:
            raise TypeError('Invalid type for cluster_id')
        if type(namespace) != str:
            raise TypeError('Invalid type for namespace')
        if type(daemonset) != str:
            raise TypeError('Invalid type for daemonset')

        # create request
        path = '/cluster/{cluster}/namespace/{namespace}/daemonset/{daemonset}'.format(cluster=cluster_id,
                                                                                       namespace=namespace,
                                                                                       daemonset=daemonset)
        request = ClusterAgent.delete_request(path)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def validate_resource_manifest_file(cluster_id: str, file_path: str) -> str:
        """
        validate resource manifest file
        :param cluster_id: (str) cluster name
        :param file_path: (str) file path transferred
        :return: (str) request_id
        """
        if type(cluster_id) != str:
            raise TypeError('Invalid type for cluster_id')
        if type(file_path) != str:
            raise TypeError('Invalid type for file_path')
        if not os.path.isfile(file_path):
            raise FileNotFoundError('Invalid file: {}'.format(file_path))

        # set transfer file to request body
        file_content = FileContent()
        file_content.load(file_path)
        manifest = Content()
        manifest.set_content_type(ContentType.FILE.value)
        manifest.append_content(file_content)

        # create request
        path = '/cluster/{cluster}/manifest/validate'.format(cluster=cluster_id)
        body = {'manifest': manifest}
        request = ClusterAgent.post_request(path, body)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def validate_resource_manifest_stream(cluster_id: str, buffer: bytes, filename: str) -> str:
        """
        validate resource manifest file
        :param cluster_id: (str) cluster name
        :param buffer: (bytes) file stream
        :param filename: (str) filename
        :return: (str) request_id
        """
        if type(cluster_id) != str:
            raise TypeError('Invalid type for cluster_id')
        if type(filename) != str:
            raise TypeError('Invalid type for filename')

        # set transfer file to request body
        file_content = FileContent()
        file_content.loads(buffer, filename)
        manifest = Content()
        manifest.set_content_type(ContentType.FILE.value)
        manifest.append_content(file_content)

        # create request
        path = '/cluster/{cluster}/manifest/validate'.format(cluster=cluster_id)
        body = {'manifest': manifest}
        request = ClusterAgent.post_request(path, body)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def apply_resource_manifest_file(cluster_id: str, file_path: str) -> str:
        """
        apply resource manifest file
        :param cluster_id: (str) cluster name
        :param file_path: (str) file path transferred
        :return: (str) request_id
        """
        if type(cluster_id) != str:
            raise TypeError('Invalid type for cluster_id')
        if type(file_path) != str:
            raise TypeError('Invalid type for file_path')
        if not os.path.isfile(file_path):
            raise FileNotFoundError('Invalid file: {}'.format(file_path))

        # set transfer file to request body
        file_content = FileContent()
        file_content.load(file_path)
        manifest = Content()
        manifest.set_content_type(ContentType.FILE.value)
        manifest.append_content(file_content)

        # create request
        path = '/cluster/{cluster}' \
               '/manifest/apply'.format(cluster=cluster_id)
        body = {'manifest': manifest}
        request = ClusterAgent.post_request(path, body)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def apply_resource_manifest_stream(cluster_id: str,
                                       buffer: bytes,
                                       filename: str) -> str:
        """
        apply resource manifest file
        :param cluster_id: (str) cluster name
        :param buffer: (bytes) file stream
        :param filename: (str) filename
        :return: (str) request_id
        """
        if type(cluster_id) != str:
            raise TypeError('Invalid type for cluster_id')
        if type(filename) != str:
            raise TypeError('Invalid type for filename')

        # set transfer file to request body
        manifest = Content()
        manifest.set_content_type(ContentType.FILE.value)

        file_content = FileContent()
        file_content.loads(buffer, filename)
        manifest.append_content(file_content)

        # create request
        path = '/cluster/{cluster}/manifest/apply'.format(cluster=cluster_id)
        body = {'manifest': manifest}

        request = ClusterAgent.post_request(path, body)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def delete_resource_manifest_file(cluster_id: str, file_path: str) -> str:
        """
        delete resource manifest
        :param cluster_id: (str) cluster name
        :param file_path: (str) file path transferred
        :return: (str) request_id
        """
        if type(cluster_id) != str:
            raise TypeError('Invalid type for cluster_id')
        if type(file_path) != str:
            raise TypeError('Invalid type for file_path')
        if not os.path.isfile(file_path):
            raise FileNotFoundError('Invalid file: {}'.format(file_path))

        # set transfer file to request body
        file_content = FileContent()
        file_content.load(file_path)
        content = Content()
        content.set_content_type(ContentType.FILE.value)
        content.append_content(file_content)

        # create request
        path = '/cluster/{cluster}/manifest/delete'.format(cluster=cluster_id)
        body = {'manifest': content}
        request = ClusterAgent.post_request(path, body)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def delete_resource_manifest_stream(cluster_id: str, buffer: bytes, filename: str) -> str:
        """
        delete resource manifest
        :param cluster_id: (str) cluster name
        :param buffer: (bytes) file stream
        :param filename: (str) filename
        :return: (str) request_id
        """
        if type(cluster_id) != str:
            raise TypeError('Invalid type for cluster_id')
        if type(filename) != str:
            raise TypeError('Invalid type for filename')

        # set transfer file to request body
        file_content = FileContent()
        file_content.loads(buffer, filename)
        content = Content()
        content.set_content_type(ContentType.FILE.value)
        content.append_content(file_content)

        # create request
        path = '/cluster/{cluster}/manifest/delete'.format(cluster=cluster_id)
        body = {'manifest': content}
        request = ClusterAgent.post_request(path, body)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def get_request_status(cluster_id: str, request_id: str) -> str:
        """
        get request status
        :param cluster_id: (str) cluster name
        :param request_id: (str) request ID
        :return:
        """
        if type(cluster_id) != str:
            raise TypeError('Invalid type for cluster_id')
        if type(request_id) != str:
            raise TypeError('Invalid type for request_id')

        # create request
        path = '/cluster/{cluster}/request/{request}'.format(cluster=cluster_id,
                                                             request=request_id)
        request = ClusterAgent.get_request(path)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def export_service(cluster_id: str, namespace: str, service: str) -> str:
        """
        export service
        :param cluster_id: (str) cluster name
        :param namespace: (str) namespace name
        :param service: (str) service name
        :return: (str) request_id
        """
        if type(cluster_id) != str:
            raise TypeError('Invalid type for cluster_id')

        if type(namespace) != str:
            raise TypeError('Invalid type for namespace')

        if type(service) != str:
            raise TypeError('Invalid type for service')

        # create request
        path = '/cluster/{cluster}/namespace/{namespace}/service/{service}/export'.format(cluster=cluster_id,
                                                                                          namespace=namespace,
                                                                                          service=service)
        request = ClusterAgent.post_request(path, None)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def unexport_service(cluster_id: str, namespace: str, service: str) -> str:
        """
        unexport service
        :param cluster_id: (str) cluster name
        :param namespace: (str) namespace name
        :param service: (str) service name
        :return: (str) request_id
        """
        if type(cluster_id) != str:
            raise TypeError('Invalid type for cluster_id')

        if type(namespace) != str:
            raise TypeError('Invalid type for namespace')

        if type(service) != str:
            raise TypeError('Invalid type for service')

        # create request
        path = '/cluster/{cluster}/namespace/{namespace}/service/{service}/unexport'.format(cluster=cluster_id,
                                                                                            namespace=namespace,
                                                                                            service=service)
        request = ClusterAgent.post_request(path, None)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def update_remote_broker(cluster_name: str, broker_info_text: str) -> str:
        """
        update remote broker_info
        :param cluster_name: (str) cluster name
        :param broker_info_text: (str) submariner broker.info file content
        :return:
        """
        body = {}

        if type(cluster_name) != str:
            raise TypeError('Invalid type for cluster_name')

        if not broker_info_text:
            raise ValueError('Invalid broker info')

        if type(broker_info_text) != str:
            raise ValueError('Invalid broker info')

        if len(broker_info_text) <= 0:
            raise ValueError('Invalid broker info')

        # set transfer file to request body
        broker_info = Content()
        broker_info.set_content_type(ContentType.TEXT.value)
        broker_info.append_content(broker_info_text)
        body['broker_info'] = broker_info

        # create request
        path = '/cluster/{cluster}/mcn/broker/update'.format(cluster=cluster_name)
        request = ClusterAgent.post_request(path, body)

        # emit request
        Publisher().emit(cluster_name, request)

        return request.get_request_id()

    @staticmethod
    def connect_multi_cluster_network(cluster_id: str,
                                      role: str,
                                      mc_connect_id: str,
                                      remote_cluster_id: str,
                                      broker_info_text: str = None) -> str:
        """
        connect multi-cluster broker
        :param cluster_id: (str) cluster ID
        :param role:  (str) broker role MultiClusterRole(Enum).value
        :param mc_connect_id: (str) multi-cluster connection id issued from center
        :param remote_cluster_id: (str) remote cluster ID
        :param broker_info_text:  (str) submariner broker.info file content(text)
        :return:
        """
        body = {}

        if type(cluster_id) != str or not cluster_id or len(cluster_id) <= 0:
            raise TypeError('Invalid type for cluster_id, cluster_id=' + cluster_id)

        if not MultiClusterRole.validate(role):
            raise ValueError('Invalid value for role: {}'.format(role))

        if type(mc_connect_id) != str or not mc_connect_id or len(mc_connect_id) <= 0:
            raise TypeError('Invalid type for mc_connect_id, mc_connect_id=' + mc_connect_id)

        if role == MultiClusterRole.REMOTE.value:
            if not broker_info_text:
                raise ValueError('Invalid broker info')
            if type(broker_info_text) != str:
                raise ValueError('Invalid broker info')
            if len(broker_info_text) <= 0:
                raise ValueError('Invalid broker info')

        # set transfer file to request body
        broker_role_content = Content()
        broker_role_content.set_content_type(ContentType.TEXT.value)
        broker_role_content.append_content(role)
        body['role'] = broker_role_content

        # set mc_connect_id to request body
        mc_connect_id_content = Content()
        mc_connect_id_content.set_content_type(ContentType.TEXT.value)
        mc_connect_id_content.append_content(mc_connect_id)
        body['mc_connect_id'] = mc_connect_id_content

        if role == MultiClusterRole.REMOTE.value:
            # set transfer file to request body
            broker_info = Content()
            broker_info.set_content_type(ContentType.TEXT.value)
            broker_info.append_content(broker_info_text)
            body['broker_info'] = broker_info

        # set remote_cluster_id to request body
        remote_cluster_id_content = Content()
        remote_cluster_id_content.set_content_type(ContentType.TEXT.value)
        remote_cluster_id_content.append_content(remote_cluster_id)
        body['remote_cluster_id'] = remote_cluster_id_content

        # create request
        path = '/cluster/{cluster}/mcn/broker/connect'.format(cluster=cluster_id)
        request = ClusterAgent.post_request(path, body)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def disconnect_multi_cluster_network(cluster_id: str,
                                         connect_id) -> str:
        """
        disconnect multi-cluster network
        :param cluster_id: (str) cluster name
        :param connect_id: (str) multi-cluster connect id
        :return:
        """
        # create request
        path = '/cluster/{cluster}/mcn/broker/disconnect'.format(cluster=cluster_id)
        # set transfer file to request body
        mc_connect_id = Content()
        mc_connect_id.set_content_type(ContentType.TEXT.value)
        mc_connect_id.append_content(connect_id)
        body = {'mc_connect_id': connect_id}

        request = ClusterAgent.post_request(path, body)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def get_broker_info(cluster_id: str) -> str:
        """
        get cluster submariner's broker-info.subm
        :param cluster_id: (str) cluster name
        :return:
        """
        # create request
        path = '/cluster/{cluster}/mcn/broker'.format(cluster=cluster_id)
        request = ClusterAgent.get_request(path)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def get_broker_status(cluster_id: str) -> str:
        """
        get cluster submariner's status
        :param cluster_id: (str) cluster name
        :return:
        """
        # create request
        path = '/cluster/{cluster}/mcn/broker/status'.format(cluster=cluster_id)
        request = ClusterAgent.get_request(path)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def remove_agent(cluster_id: str) -> str:
        """
        remove cluster agent
        :param cluster_id: (str) cluster name
        :return: (str) request id
        """
        # create request
        path = '/cluster/{cluster}'.format(cluster=cluster_id)
        request = ClusterAgent.delete_request(path)

        # emit request
        Publisher().emit(cluster_id, request)

        return request.get_request_id()

    @staticmethod
    def create_snapshot(migration_id: str,
                        source_cluster_name: str,
                        source_cluster_role: str,
                        target_cluster_name: str,
                        source_namespace: str,
                        source_pod: str) -> str:
        """
        create snapshot
        :param migration_id: (str) migration id
        :param source_cluster_name: (str) source cluster name
        :param source_cluster_role: (str) source cluster role
        :param target_cluster_name: (str) target cluster name
        :param source_namespace: (str) source namespace name
        :param source_pod: (str) source pod name
        :return: (str) request id
        """
        # create request
        path = '/cluster/{cluster}/namespace/{namespace}/pod/{pod}/migrate/snapshot'\
            .format(cluster=source_cluster_name,
                    namespace=source_namespace,
                    pod=source_pod)

        body = {}

        # set request body
        migration_id_content = Content()
        migration_id_content.set_content_type(ContentType.TEXT.value)
        migration_id_content.append_content(migration_id)
        body['migration_id'] = migration_id_content

        source_cluster_role_content = Content()
        source_cluster_role_content.set_content_type(ContentType.TEXT.value)
        source_cluster_role_content.append_content(source_cluster_role)
        body['source_cluster_role'] = source_cluster_role_content

        target_cluster_name_content = Content()
        target_cluster_name_content.set_content_type(ContentType.TEXT.value)
        target_cluster_name_content.append_content(target_cluster_name)
        body['target_cluster_name'] = target_cluster_name_content

        request = ClusterAgent.post_request(path, body)

        # emit request
        Publisher().emit(source_cluster_name, request)

        return request.get_request_id()

    @staticmethod
    def validate_snapshot(migration_id: str,
                          source_cluster_name: str,
                          source_cluster_role: str,
                          target_cluster_name: str,
                          source_namespace: str,
                          source_pod: str) -> str:
        """
        validate snapshot created
        :param migration_id: (str) migration id
        :param source_cluster_name: (str) source cluster name
        :param source_cluster_role: (str) source cluster role
        :param target_cluster_name: (str) target cluster name
        :param source_namespace: (str) source namespace name
        :param source_pod: (str) source pod name
        :return: (str) request id
        """
        # create request
        path = '/cluster/{cluster}/namespace/{namespace}/pod/{pod}/migrate/validate_snapshot'\
            .format(cluster=source_cluster_name,
                    namespace=source_namespace,
                    pod=source_pod)
        body = {}

        # set request body
        migration_id_content = Content()
        migration_id_content.set_content_type(ContentType.TEXT.value)
        migration_id_content.append_content(migration_id)
        body['migration_id'] = migration_id_content

        source_cluster_role_content = Content()
        source_cluster_role_content.set_content_type(ContentType.TEXT.value)
        source_cluster_role_content.append_content(source_cluster_role)
        body['source_cluster_role'] = source_cluster_role_content

        target_cluster_name_content = Content()
        target_cluster_name_content.set_content_type(ContentType.TEXT.value)
        target_cluster_name_content.append_content(target_cluster_name)
        body['target_cluster_name'] = target_cluster_name_content

        request = ClusterAgent.post_request(path, body)

        # emit request
        Publisher().emit(source_cluster_name, request)

        return request.get_request_id()


    @staticmethod
    def restore_snapshot(migration_id: str,
                         source_cluster_name: str,
                         source_cluster_role: str,
                         target_cluster_name: str,
                         target_node_name: str,
                         source_namespace: str,
                         source_pod: str):
        """
        restore snapshot
        :param migration_id: (str) migration id
        :param source_cluster_name: (str) source cluster name
        :param source_cluster_role: (str) source cluster role
        :param target_cluster_name: (str) target cluster name
        :param target_node_name: (str) target node name
        :param source_namespace: (str) source namespace name
        :param source_pod: (str) source pod name
        :return: (str) request id
        """
        # create request
        path = '/cluster/{cluster}/namespace/{namespace}/pod/{pod}/migrate/restore' \
            .format(cluster=target_cluster_name,
                    namespace=source_namespace,
                    pod=source_pod)
        body = {}

        # set request body
        migration_id_content = Content()
        migration_id_content.set_content_type(ContentType.TEXT.value)
        migration_id_content.append_content(migration_id)
        body['migration_id'] = migration_id_content

        source_cluster_name_content = Content()
        source_cluster_name_content.set_content_type(ContentType.TEXT.value)
        source_cluster_name_content.append_content(source_cluster_name)
        body['source_cluster_name'] = source_cluster_name_content

        source_cluster_role_content = Content()
        source_cluster_role_content.set_content_type(ContentType.TEXT.value)
        source_cluster_role_content.append_content(source_cluster_role)
        body['source_cluster_role'] = source_cluster_role_content

        target_node_name_content = Content()
        target_node_name_content.set_content_type(ContentType.TEXT.value)
        target_node_name_content.append_content(target_node_name)
        body['target_node_name'] = target_node_name_content

        request = ClusterAgent.post_request(path, body)

        # emit request
        Publisher().emit(target_cluster_name, request)

        return request.get_request_id()


    @staticmethod
    def validate_restored_snapshot(migration_id: str,
                                   target_cluster_name: str,
                                   target_node_name: str,
                                   source_cluster_name: str,
                                   source_cluster_role: str,
                                   source_namespace: str,
                                   source_pod: str):
        """
        validate restored snapshot
        :param migration_id: (str) migration id
        :param target_cluster_name: (str) target cluster name
        :param target_node_name: (str) target node name
        :param source_cluster_name: (str) source cluster name
        :param source_cluster_role: (str) source cluster role
        :param source_namespace: (str) namespace name
        :param source_pod: (str) pod name
        :return:
        """
        # create request
        path = '/cluster/{cluster}/namespace/{namespace}/pod/{pod}/migrate/validate_restore'\
            .format(cluster=target_cluster_name,
                    namespace=source_namespace,
                    pod=source_pod)

        body = {}

        # set request body
        migration_id_content = Content()
        migration_id_content.set_content_type(ContentType.TEXT.value)
        migration_id_content.append_content(migration_id)
        body['migration_id'] = migration_id_content

        target_node_name_content = Content()
        target_node_name_content.set_content_type(ContentType.TEXT.value)
        target_node_name_content.append_content(target_node_name)
        body['target_node_name'] = target_node_name_content

        source_cluster_name_content = Content()
        source_cluster_name_content.set_content_type(ContentType.TEXT.value)
        source_cluster_name_content.append_content(source_cluster_name)
        body['source_cluster_name'] = source_cluster_name_content

        source_cluster_role_content = Content()
        source_cluster_role_content.set_content_type(ContentType.TEXT.value)
        source_cluster_role_content.append_content(source_cluster_role)
        body['source_cluster_role'] = source_cluster_role_content

        request = ClusterAgent.post_request(path, body)

        # emit request
        Publisher().emit(target_cluster_name, request)

        return request.get_request_id()

    @staticmethod
    def delete_migration_source(migration_id: str,
                                source_cluster_name: str,
                                source_namespace: str,
                                source_pod) -> str:
        """
        delete migration source(pod, snapshot CRD)
        :param migration_id: (str) migration id
        :param source_cluster_name: (str) source cluster name
        :param source_namespace: (str) source namespace
        :param source_pod: (str) source pod
        :return:
        (str) request_id
        """
        # create request
        path = '/cluster/{cluster}/namespace/{namespace}/pod/{pod}/migrate/delete_migration_source'\
            .format(cluster=source_cluster_name,
                    namespace=source_namespace,
                    pod=source_pod)

        body = {}

        # set request body
        migration_id_content = Content()
        migration_id_content.set_content_type(ContentType.TEXT.value)
        migration_id_content.append_content(migration_id)
        body['migration_id'] = migration_id_content

        request = ClusterAgent.post_request(path, body)

        # emit request
        Publisher().emit(source_cluster_name, request)

        return request.get_request_id()