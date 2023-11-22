import gc

import six

from gwlink_manager.settings import get_logger
from repository.common.type import Kubernetes
from repository.model.k8s.daemonset import DaemonSet
from repository.model.k8s.deployment import Deployment
from repository.model.k8s.namespace import Namespace
from repository.model.k8s.node import Node
from repository.model.k8s.pod import Pod
from repository.model.k8s.service import Service


class Cluster:
    """
    CEdge cluster model
    """

    def __init__(self, cluster_id):
        """
        Cluster()
        :param cluster_id: (str)
        """
        self._cluster_id = cluster_id
        self._multi_cluster_id = None
        self._multi_cluster = []
        self._nodes = []
        self._components = []
        self._namespaces = []
        self._services = []
        self._pods = []
        self._daemonsets = []
        self._deployments = []
        self._logger = get_logger(__name__)

    def set_cluster_id(self, cluster_id):
        """
        set cluster id
        :param cluster_id: (str)
        :return:
        """
        self.cluster_id = cluster_id

    def get_cluster_id(self):
        """
        get cluster id
        :return: (str) cluster_id
        """
        return self.cluster_id

    def create_or_update(self, resource):
        """
        create or update resource
        :param resource: (object) Node or Namespace or Pod or Service or Deployment or Daemonset
        :return:
        """
        if type(resource) == Node:
            iterate_item = self._nodes
        elif type(resource) == Namespace:
            iterate_item = self._namespaces
        elif type(resource) == Pod:
            iterate_item = self._pods
        elif type(resource) == Deployment:
            iterate_item = self._deployments
        elif type(resource) == DaemonSet:
            iterate_item = self._daemonsets
        elif type(resource) == Service:
            iterate_item = self._services
        else:
            raise ValueError('Invalid resource')

        index = -1
        for i in range(0, len(iterate_item)):
            if iterate_item[i].name == resource.name:
                index = i
        # print(resource.to_dict())

        # create or update resource
        if index >= 0:
            if iterate_item[index]:
                iterate_item[index] = None

            iterate_item[index] = resource
        else:
            iterate_item.append(resource)

    def delete(self, resource):
        """
        delete resource
        :param resource: (object) Node or Namespace or Pod or Service or Deployment or Daemonset
        :return:
            (str) resource name
            (str) resource kind
        """
        iterate_item = None

        if not hasattr(resource, 'to_dict') or 'kind' not in resource.to_dict():
            raise KeyError('Invalid resource')

        resource_dict = resource.to_dict()
        if resource_dict['kind'] == Kubernetes.NODE.value:
            iterate_item = self._nodes
        elif resource_dict['kind'] == Kubernetes.NAMESPACE.value:
            iterate_item = self._namespaces
        elif resource_dict['kind'] == Kubernetes.POD.value:
            iterate_item = self._pods
        elif resource_dict['kind'] == Kubernetes.DEPLOYMENT.value:
            iterate_item = self._deployments
        elif resource_dict['kind'] == Kubernetes.DAEMONSET.value:
            iterate_item = self._daemonsets
        elif resource_dict['kind'] == Kubernetes.SERVICE.value:
            iterate_item = self._services
        else:
            self._logger.info('Not support Kubernetes resource kind=({})'.format(resource['kind']))

        index = -1
        name = resource_dict['metadata']['name']
        for i in range(0, len(iterate_item)):
            if iterate_item[i].name == name:
                index = i

        # delete
        if index > 0:
            del iterate_item[index]

        return name, resource_dict['kind']

    def get_nodes(self):
        """
        get all node list
        :return:
        """
        return self._nodes

    def get_k8s_version(self):
        """
        get k8s version
        :return:
        """
        for node in self._nodes:
            k8s_version = node.get_k8s_version()
            if k8s_version is not None:
                return k8s_version

        return None

    def get_pods(self):
        """
        get pods from repository
        :return:
        """
        return self._pods

    def get_services(self):
        """
        get services from repository
        :return:
        """
        return self._services

    def get_daemonsets(self):
        """
        get daemonsets from repository
        :return:
        """
        return self._daemonsets

    def get_namespaces(self):
        """
        get all namespace list
        :return: (list(Namespace))
        """
        return self._namespaces

    def get_components(self):
        """
        get all components
        :return:
        """
        return self._components

    def get_all_services(self):
        """
        get all services
        :return:
        """
        return self._services

    def get_namespaced_services(self, namespace):
        """
        get namespaced services
        :param namespace: (str)
        :return:
        """
        pass

    def get_service(self, namespace, service):
        """
        get service
        :param namespace: (str) namespace name
        :param service: (str) service name
        :return:
        """
        pass

    def get_all_pods(self):
        """
        get all pods
        :return:
        """
        return self._pods

    def get_all_daemonsets(self):
        """
        get all daemonsets
        :return:
        """
        return self._daemonsets

    def get_all_deployments(self):
        """
        get all deployments
        :return:
        """
        return self._deployments

    def get_multicluster(self):
        """
        get multi-cluster metric
        :return:
        """
        return self._multi_cluster

    def get_multicluster_id(self):
        """
        get multi-cluster id
        :return:
        """
        return self._multi_cluster_id
