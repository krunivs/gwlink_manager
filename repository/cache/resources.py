from typing import List

from gwlink_manager.settings import get_logger
from repository.common.type import PodStatus
from repository.model.k8s.daemonset import DaemonSet
from repository.model.k8s.deployment import Deployment
from repository.model.k8s.namespace import Namespace
from repository.model.k8s.node import Node
from repository.model.k8s.pod import Pod
from repository.model.k8s.service import Service

class ResourceCache(object):
    """
    Kubernetes resource management class
    """
    _logger = None
    _connector = None
    _cluster_id = None
    _nodes = []
    _daemonsets = []
    _deployments = []
    _namespaces = []
    _pods = []
    _services = []
    _custom_objects = []

    def __init__(self):
        self.clear()
        self._logger = get_logger(__name__)

    def clear(self):
        """
        clear entire cache
        :return:
        """
        self._nodes = []
        self._daemonsets = []
        self._deployments = []
        self._namespaces = []
        self._pods = []
        self._services = []
        self._custom_objects = []

    def set_cluster_id(self, cluster_id: str):
        """
        set cluster id
        :param cluster_id: (str)
        :return:
        """
        self._cluster_id = cluster_id

    def get_cluster_id(self) -> str:
        """
        get cluster id
        :return:
        """
        return self._cluster_id

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

        if hasattr(resource, 'namespace'):
            for i in range(0, len(iterate_item)):
                if iterate_item[i].name == resource.name and \
                        iterate_item[i].namespace == resource.namespace:
                    index = i
        else:
            for i in range(0, len(iterate_item)):
                if iterate_item[i].name == resource.name:
                    index = i

        # create or update resource
        if index >= 0:
            if iterate_item[index]:
                iterate_item[index] = None
                iterate_item[index] = resource

            iterate_item[index] = resource
        else:
            iterate_item.append(resource)

    def delete(self, resource: object):
        """
        delete resource
        :param resource: (object)
        :return:
        """
        name = resource.get_name()
        namespace = None
        kind = resource.get_kind()

        if type(resource) == Node:
            iterate_item = self._nodes

        elif type(resource) == Namespace:
            iterate_item = self._namespaces

        elif type(resource) == Pod:
            iterate_item = self._pods
            namespace = resource.get_namespace()

        elif type(resource) == Deployment:
            iterate_item = self._deployments
            namespace = resource.get_namespace()

        elif type(resource) == DaemonSet:
            iterate_item = self._daemonsets
            namespace = resource.get_namespace()

        elif type(resource) == Service:
            iterate_item = self._services
            namespace = resource.get_namespace()

        else:
            # exc4
            self._logger.error('Not support Kubernetes resource. '
                               'kind={}, name={}, namespace={}'.format(kind, name, namespace))
            return

        index = -1

        if namespace and iterate_item:
            for i in range(0, len(iterate_item)):
                if iterate_item[i].name == name and iterate_item[i].namespace == namespace:
                    index = i
        else:
            # in case of class Namespace
            for i in range(0, len(iterate_item)):
                if iterate_item[i].name == name:
                    index = i
        # delete
        if index > 0:
            del iterate_item[index]

        return

    def get_number_of_nodes(self) -> int:
        """
        get number of nodes
        :return:
        """
        return len(self._nodes)

    def get_nodes(self) -> List[Node]:
        """
        get nodes from repository
        :return:
        """
        return self._nodes

    def set_nodes(self, val: List[Node]):
        """
        set node list to repository
        :param val: (List[Node])
        :return:
        """
        if type(val) != list:
            raise TypeError('Invalid type. Must input List[Node]')

        for item in val:
            if type(item) != Node:
                raise TypeError('Invalid type. Must input List[Node]')

        if self._nodes:
            self._nodes.clear()

        self._nodes = val

    def get_node(self, node_name: str) -> Node:
        """
        get node by node_name
        :param node_name: (str)
        :return:
        """
        found = -1

        if type(node_name) != str:
            raise TypeError('Invalid parameter(node_name) type')

        for i in range(0, len(self._nodes)):
            if self._nodes[i].get_name() == node_name:
                found = i
                break

        if found < 0:
            return None

        return self._nodes[found]

    def get_master_node(self) -> Node:
        """
        get master node
        :return:
        """
        master_node = None

        for node in self._nodes:
            if node.get_role() == 'Master':
                master_node = node
                break

        return master_node

    def get_k8s_version(self) -> str:
        """
        get k8s version
        :return:
        """
        for node in self._nodes:
            k8s_version = node.get_k8s_version()
            if k8s_version is not None:
                return k8s_version

        return None

    def set_namespaces(self, val: List[Namespace]):
        """
        set namespace list
        :param val: (List[Namespace])
        :return:
        """
        if type(val) != list:
            raise TypeError('Invalid type. Must input List[Namespace]')

        for item in val:
            if type(item) != Namespace:
                raise TypeError('Invalid type. Must input List[Namespace]')

        if self._namespaces:
            self._namespaces.clear()

        self._namespaces = val

    def get_namespaces(self) -> List[Namespace]:
        """
        get namespaces from repository
        :return: list[Namespace]
        """
        return self._namespaces

    def get_all_namespace_pods(self) -> List[Pod]:
        """
        get pods from repository
        :return: list[Pod]
        """
        return self._pods

    def get_all_namespace_pods_by_pod(self, pod: str) -> List[Pod]:
        """
        get all pod filtrated by pod name
        :param pod: (str) pod name
        :return: (List[Pod])
        """
        filtrated_pods = []

        for item in self._pods:
            if item.get_name() == pod:
                filtrated_pods.append(item)

        return filtrated_pods

    def get_all_namespace_pods_by_service(self, service: str) -> List[Pod]:
        """
        get all pod filtrated by service name
        :param service: (str) service name
        :return: (List[Pod])
        """
        filtrated_pods = []
        filtrated_services = []

        # select services for service name
        for item in self._services:
            if item.get_name() == service:
                filtrated_services.append(item)

        # select pods for service's label selector
        for item in filtrated_services:
            selectors = item.get_selector()
            if selectors is None or len(selectors) <= 0:
                continue
            for pod in self._pods:
                if item.get_namespace() == pod.get_namespace():
                    labels = pod.get_labels()
                    if labels is None or len(labels) <= 0:
                        continue
                    for label in labels:
                        if label in selectors:
                            filtrated_pods.append(pod)
                            break

        return filtrated_pods

    def set_deployments(self, val: List[Deployment]):
        """
        set deployment list to repository
        :param val: (List[Deployment])
        :return:
        """
        if type(val) != list:
            raise TypeError('Invalid type. Must input List[Deployment]')

        for item in val:
            if type(item) != Deployment:
                raise TypeError('Invalid type. Must input List[Deployment]')

        if self._deployments:
            self._deployments.clear()

        self._deployments = val

    def get_all_namespace_pods_by_deployment(self, deployment: str) -> List[Pod]:
        """
        get namespace pod filtrated by deployment name
        :param deployment: (str) deployment name
        :return: (List[Pod])
        """
        filtrated_pods = []
        filtrated_deployments = []

        # select deployments for deployment name
        for item in self._deployments:
            if item.get_name() == deployment:
                filtrated_deployments.append(item)

        # select pods for deployment's label selector
        for item in filtrated_deployments:
            selectors = item.get_selector()
            if selectors is None or len(selectors) <= 0:
                continue
            for pod in self._pods:
                if item.get_namespace() == pod.get_namespace():
                    labels = pod.get_labels()
                    if labels is None or len(labels) <= 0:
                        continue
                    for label in labels:
                        if label in selectors:
                            filtrated_pods.append(pod)
                            break

        return filtrated_pods

    def get_all_namespace_pods_by_daemonset(self, deamonset: str) -> List[Pod]:
        """
        get namespace pod filtrated by deamonset name
        :param deamonset: (str) deamonset name
        :return: (List[Pod])
        """
        filtrated_pods = []
        filtrated_deamonsets = []

        # select daemonsets for deamonset name
        for item in self._daemonsets:
            if item.get_name() == deamonset:
                filtrated_deamonsets.append(item)

        # select pods for deamonset label selector
        for item in filtrated_deamonsets:
            selectors = item.get_selector()
            if selectors is None or len(selectors) <= 0:
                continue
            for pod in self._pods:
                if item.get_namespace() == pod.get_namespace():
                    labels = pod.get_labels()
                    if labels is None or len(labels) <= 0:
                        continue
                    for label in labels:
                        if label in selectors:
                            filtrated_pods.append(pod)
                            break

        return filtrated_pods

    def get_namespace_pods(self, namespace: str) -> List[Pod]:
        """
        get namespace pods from repository
        :return: list[Pod]
        """
        pods = []

        if type(namespace) != str or len(namespace) <= 0:
            raise ValueError('Invalid parameter(namespace) value')

        for pod in self._pods:
            if pod.get_namespace() == namespace:
                pods.append(pod)

        return pods

    def get_namespace_pods_by_pod(self,
                                  namespace: str,
                                  pod: str) -> List[Pod]:
        """
        get all pod filtrated by pod name
        :param namespace: (str) namespace name
        :param pod: (str) pod name
        :return: (List[Pod])
        """
        filtrated_pods = []
        namespace_pods = self.get_namespace_pods(namespace)

        for item in namespace_pods:
            if item.get_name() == pod:
                filtrated_pods.append(item)

        return filtrated_pods

    def get_namespace_pods_by_service(self,
                                      namespace: str,
                                      service: str) -> List[Pod]:
        """
        get namespace pod filtrated by service name
        :param namespace: (str) namespace name
        :param service: (str) service name
        :return: (List[Pod])
        """
        filtrated_pods = []
        filtrated_services = []
        namespace_pods = self.get_namespace_pods(namespace)

        if len(namespace_pods) == 0:
            return []

        # select service for service name
        for item in self._services:
            if item.get_name() == service:
                filtrated_services.append(item)

        # select pods for service's label selector
        for item in filtrated_services:
            selectors = item.get_selector()
            if selectors is None or len(selectors) <= 0:
                continue

            for pod in namespace_pods:
                if item.get_namespace() == pod.get_namespace():
                    labels = pod.get_labels()
                    if labels is None or len(labels) <= 0:
                        continue
                    for label in labels:
                        if label in selectors:
                            filtrated_pods.append(pod)
                            break

        return filtrated_pods

    def get_namespace_pods_by_deployment(self,
                                         namespace: str,
                                         deployment: str) -> List[Pod]:
        """
        get namespace pod filtrated by deployment name
        :param namespace: (str) namespace name
        :param deployment: (str) deployment name
        :return: (List[Pod])
        """
        filtrated_pods = []
        filtrated_deployments = []
        namespace_pods = self.get_namespace_pods(namespace)

        if len(namespace_pods) == 0:
            return []

        # select deployment for deployment name
        for item in self._deployments:
            if item.get_name() == deployment:
                filtrated_deployments.append(item)

        # select pods for deployment's label selector
        for item in filtrated_deployments:
            selectors = item.get_selector()
            if selectors is None or len(selectors) <= 0:
                continue

            for pod in namespace_pods:
                if item.get_namespace() == pod.get_namespace():
                    labels = pod.get_labels()
                    if labels is None or len(labels) <= 0:
                        continue
                    for label in labels:
                        if label in selectors:
                            filtrated_pods.append(pod)
                            break

        return filtrated_pods

    def get_namespace_pods_by_daemonset(self,
                                        namespace: str,
                                        daemonset: str) -> List[Pod]:
        """
        get namespace pod filtrated by deamonset name
        :param namespace: (str) namespace name
        :param daemonset: (str) daemonset name
        :return: (List[Pod])
        """
        filtrated_pods = []
        filtrated_daemonsets = []
        namespace_pods = self.get_namespace_pods(namespace)

        if len(namespace_pods) == 0:
            return []

        # select daemonset for daemonset name
        for item in self._daemonsets:
            if item.get_name() == daemonset:
                filtrated_daemonsets.append(item)

        # select pods for daemonset label selector
        for item in filtrated_daemonsets:
            selectors = item.get_selector()
            if selectors is None or len(selectors) <= 0:
                continue

            for pod in namespace_pods:
                if item.get_namespace() == pod.get_namespace():
                    labels = pod.get_labels()
                    if labels is None or len(labels) <= 0:
                        continue
                    for label in labels:
                        if label in selectors:
                            filtrated_pods.append(pod)
                            break

        return filtrated_pods

    def set_services(self, val: List[Service]):
        """
        set service list to repository
        :param val: (List[Service])
        :return:
        """
        if type(val) != list:
            raise TypeError('Invalid type. Must input List[Service]')

        for item in val:
            if type(item) != Service:
                raise TypeError('Invalid type. Must input List[Service]')

        if self._services:
            self._services.clear()

        self._services = val

    def get_all_namespace_services(self) -> List[Service]:
        """
        get services from repository
        :return: list[Service]
        """
        return self._services

    def get_all_namespace_services_by_service(self,
                                              service: str) -> List[Service]:
        """
        get all namespace service by service name
        :param service: (str) service name
        :return: List[Service]
        """
        services = []
        for item in self._services:
            if item.get_name() == service:
                services.append(item)

        return services

    def get_all_namespace_services_by_pod(self, pod: str) -> List[Service]:
        """
        get all namespace service by pod name
        :param pod: (str) pod name
        :return: List[Service]
        """
        filtrated_pods = []
        filtrated_services = []

        # select pod for pod name
        for item in self._pods:
            if item.get_name() == pod:
                filtrated_pods.append(item)

        # select service for pod's label
        for item in filtrated_pods:
            labels = item.get_labels()
            if labels is None or len(labels) <= 0:
                continue
            for service in self._services:
                if item.get_namespace() == service.get_namespace():
                    selectors = service.get_selector()
                    if selectors is None or len(selectors) <= 0:
                        continue
                    for selector in selectors:
                        if selector in labels:
                            filtrated_services.append(service)
                            break

        return filtrated_services

    def get_namespace_services(self, namespace: str) -> List[Service]:
        """
        get namespace services from repository
        :return: list[Service]
        """
        services = []

        if type(namespace) != str or len(namespace) <= 0:
            raise ValueError('Invalid parameter(namespace) value')

        for service in self._services:
            if service.get_namespace() == namespace:
                services.append(service)

        return services

    def get_namespace_services_by_service(self,
                                          namespace: str,
                                          service: str) -> List[Service]:
        """
        get namespace services by service name
        :param namespace: (str) namespace name
        :param service: (str) service name
        :return: List[Service]
        """
        filtrated_services = []
        namespace_services = self.get_namespace_services(namespace)

        for item in namespace_services:
            if item.get_name() == service:
                filtrated_services.append(item)

        return filtrated_services

    def get_namespace_services_by_pod(self,
                                      namespace: str,
                                      pod: str) -> List[Service]:
        """
        get namespace services by service name
        :param namespace: (str) namespace name
        :param pod: (str) pod name
        :return: List[Service]
        """
        filtrated_services = []
        filtrated_pods = []
        namespace_services = self.get_namespace_services(namespace)

        if len(namespace_services) == 0:
            return []

        # select pod for pod name
        for item in self._pods:
            if item.get_name() == pod:
                filtrated_pods.append(item)

        # select service for pod's label
        for item in filtrated_pods:
            labels = item.get_labels()
            if labels is None or len(labels) <= 0:
                continue
            for service in namespace_services:
                if item.get_namespace() == service.get_namespace():
                    selectors = service.get_selector()
                    if selectors is None or len(selectors) <= 0:
                        continue
                    for selector in selectors:
                        if selector in labels:
                            filtrated_services.append(service)
                            break

        return filtrated_services

    def set_daemonsets(self, val: List[DaemonSet]):
        """
        set daemonset list
        :param val: (List[DaemonSet])
        :return:
        """
        if type(val) != list:
            raise TypeError('Invalid type. Must input List[DaemonSet]')

        for item in val:
            if type(item) != DaemonSet:
                raise TypeError('Invalid type. Must input List[DaemonSet]')

        if self._daemonsets:
            self._daemonsets.clear()

        self._daemonsets = val

    def get_all_namespace_daemonsets(self) -> List[DaemonSet]:
        """
        get daemonsets from repository
        :return: list[DaemonSet]
        """
        return self._daemonsets

    def get_all_namespace_daemonsets_by_daemonset(self, daemonset: str) -> List[DaemonSet]:
        """
        get all namespace service by service name
        :param daemonset: (str) daemonset name
        :return: List[DaemonSet]
        """
        daemonsets = []
        for item in self._daemonsets:
            if item.get_name() == daemonset:
                daemonsets.append(item)

        return daemonsets

    def get_all_namespace_daemonsets_by_pod(self, pod: str) -> List[DaemonSet]:
        """
        get all namespace daemonsets by pod name
        :param pod: (str) pod name
        :return: List[DaemonSet]
        """
        filtrated_pods = []
        filtrated_daemonsets = []

        # select pod for pod name
        for item in self._pods:
            if item.get_name() == pod:
                filtrated_pods.append(item)

        # select daemonset for pod's label
        for item in filtrated_pods:
            labels = item.get_labels()
            if labels is None or len(labels) <= 0:
                continue
            for daemonset in self._daemonsets:
                if item.get_namespace() == daemonset.get_namespace():
                    selectors = daemonset.get_selector()
                    if selectors is None or len(selectors) <= 0:
                        continue
                    for selector in selectors:
                        if selector in labels:
                            filtrated_daemonsets.append(daemonset)
                            break

        return filtrated_daemonsets

    def get_namespace_daemonsets(self, namespace: str) -> List[DaemonSet]:
        """
        get namespace daemonsets from repository
        :return: list[Pod]
        """
        daemonsets = []

        if type(namespace) != str or len(namespace) <= 0:
            raise ValueError('Invalid parameter(namespace) value')

        for daemonset in self._daemonsets:
            if daemonset.get_namespace() == namespace:
                daemonsets.append(daemonset)

        return daemonsets

    def get_namespace_daemonsets_by_daemonset(self,
                                              namespace: str,
                                              daemonset: str) -> List[DaemonSet]:
        """
        get namespace daemonsets by daemonset name
        :param namespace: (str) namespace name
        :param daemonset: (str) daemonset name
        :return: List[DaemonSet]
        """
        filtrated_daemonsets = []
        namespace_daemonsets = self.get_namespace_daemonsets(namespace)

        for item in namespace_daemonsets:
            if item.get_name() == daemonset:
                filtrated_daemonsets.append(item)

        return filtrated_daemonsets

    def get_namespace_daemonsets_by_pod(self,
                                        namespace: str,
                                        pod: str) -> List[DaemonSet]:
        """
        get namespace daemonsets by daemonset name
        :param namespace: (str) namespace name
        :param pod: (str) pod name
        :return: List[DaemonSet]
        """
        filtrated_daemonsets = []
        filtrated_pods = []
        namespace_daemonsets = self.get_namespace_daemonsets(namespace)

        if len(namespace_daemonsets) == 0:
            return []

        # select pod for pod name
        for item in self._pods:
            if item.get_name() == pod:
                filtrated_pods.append(item)

        # select daemonset for pod's label
        for item in filtrated_pods:
            labels = item.get_labels()
            if labels is None or len(labels) <= 0:
                continue
            for daemonset in namespace_daemonsets:
                if item.get_namespace() == daemonset.get_namespace():
                    selectors = daemonset.get_selector()
                    if selectors is None or len(selectors) <= 0:
                        continue
                    for selector in selectors:
                        if selector in labels:
                            filtrated_daemonsets.append(daemonset)
                            break

        return filtrated_daemonsets

    def get_all_namespace_deployments(self) -> List[Deployment]:
        """
        get deployments from repository
        :return:
        """
        return self._deployments

    def get_all_namespace_deployments_by_deployment(self, deployment: str) -> List[Deployment]:
        """
        get all namespace deployment by deployment name
        :param deployment: (str) deployment name
        :return: List[Deployment]
        """
        deployments = []

        for item in self._deployments:
            if item.get_name() == deployment:
                deployments.append(item)

        return deployments

    def get_all_namespace_deployments_by_pod(self, pod: str) -> List[Deployment]:
        """
        get all namespace deployment by pod name
        :param pod: (str) pod name
        :return: List[Deployment]
        """
        filtrated_pods = []
        filtrated_deployments = []

        # select pod for pod name
        for item in self._pods:
            if item.get_name() == pod:
                filtrated_pods.append(item)

        # select deployment for pod's label
        for item in filtrated_pods:
            labels = item.get_labels()
            if labels is None or len(labels) <= 0:
                continue
            for deployment in self._deployments:
                if item.get_namespace() == deployment.get_namespace():
                    selectors = deployment.get_selector()
                    if selectors is None or len(selectors) <= 0:
                        continue
                    for selector in selectors:
                        if selector in labels:
                            filtrated_deployments.append(deployment)
                            break

        return filtrated_deployments

    def get_namespace_deployments(self, namespace: str) -> List[Deployment]:
        """
        get namespace deployments from repository
        :return: list[Pod]
        """
        deployments = []

        if type(namespace) != str or len(namespace) <= 0:
            raise ValueError('Invalid parameter(namespace) value')

        for deployment in self._deployments:
            if deployment.get_namespace() == namespace:
                deployments.append(deployment)

        return deployments

    def get_namespace_deployments_by_deployment(self,
                                                namespace: str,
                                                deployment: str) -> List[Deployment]:
        """
        get namespace deployments by deployment name
        :param namespace: (str) namespace name
        :param deployment: (str) deployment name
        :return: List[Deployment]
        """
        filtrated_deployments = []
        namespace_deployments = self.get_namespace_deployments(namespace)

        for item in namespace_deployments:
            if item.get_name() == deployment:
                filtrated_deployments.append(item)

        return filtrated_deployments

    def get_namespace_deployments_by_pod(self,
                                         namespace: str,
                                         pod: str) -> List[Deployment]:
        """
        get namespace deployments by deployment name
        :param namespace: (str) namespace name
        :param pod: (str) pod name
        :return: List[Deployment]
        """
        filtrated_deployments = []
        filtrated_pods = []
        namespace_deployments = self.get_namespace_deployments(namespace)

        if len(namespace_deployments) == 0:
            return []

        # select pod for pod name
        for item in self._pods:
            if item.get_name() == pod:
                filtrated_pods.append(item)

        # select deployment for pod's label
        for item in filtrated_pods:
            labels = item.get_labels()
            if labels is None or len(labels) <= 0:
                continue
            for deployment in namespace_deployments:
                if item.get_namespace() == deployment.get_namespace():
                    selectors = deployment.get_selector()
                    if selectors is None or len(selectors) <= 0:
                        continue
                    for selector in selectors:
                        if selector in labels:
                            filtrated_deployments.append(deployment)
                            break

        return filtrated_deployments

    def is_deployment_deployed(self,
                               namespace: str,
                               name: str) -> bool:
        """
        check whether deployment is deployed or not
        :param namespace: (str) namespace
        :param name: (str) deployment name
        :return: True - deployed, False - not deployed
        """
        found = False

        for deployment in self._deployments:
            if deployment.get_name() == name and deployment.get_namespace() == namespace:
                found = True

        return found

    def is_all_deployment_replicas_ready(self,
                                         namespace: str,
                                         name: str) -> bool:
        """
        check whether all deployment replicas are ready
        :param namespace: (str) namespace
        :param name: (str) deployment name
        :return: (bool)
        """

        deployment = None

        for item in self._deployments:
            if item.get_namespace() == namespace and item.get_name() == name:
                deployment = item
                break

        if deployment is None:
            return False

        if deployment.get_ready_replicas() == deployment.get_replicas():
            return True

        return False

    def is_daemonset_deployed(self,
                              namespace: str,
                              name: str) -> bool:
        """
        check whether daemonset is deployed or not
        :param namespace: (str) namespace
        :param name: (str) daemonset name
        :return: True - deployed, False - not deployed
        """
        found = False

        for daemonset in self._daemonsets:
            if daemonset.get_name() == name and daemonset.get_namespace() == namespace:
                found = True

        return found

    def is_all_daemonset_replicas_ready(self,
                                        namespace: str,
                                        name: str) -> bool:
        """
        check whether all daemonset replicas are ready
        :param namespace: (str) namespace
        :param name: (str) daemonset name
        :return: (bool)
        """
        daemonset = None

        for item in self._daemonsets:
            if item.get_namespace() == namespace and item.get_name() == name:
                daemonset = item
                break

        if daemonset is None:
            return False

        if daemonset.get_desired() == daemonset.get_ready():
            return True

    def is_service_deployed(self,
                            namespace: str,
                            name: str) -> bool:
        """
        check whether service is deployed or not
        :param namespace: (str) namespace
        :param name: (str) service name
        :return: True - deployed, False - not deployed
        """
        found = False

        for service in self._services:
            if service.get_name() == name and service.get_namespace() == namespace:
                found = True

        return found

    def is_pod_deployed(self,
                        namespace: str,
                        name: str) -> bool:
        """
        check whether pod is deployed not not
        :param namespace: (str) namespace
        :param name: (str) pod name
        :return:
        """
        found = False

        for pod in self._pods:
            if pod.get_name() == name and pod.get_namespace() == namespace:
                found = True

        return found

    def is_pod_running_for_prefix(self,
                                  namespace: str,
                                  prefix: str) -> bool:
        """
        check whether pod is running or not
        :param namespace: (str) namespace
        :param prefix: (str) pod name prefix, i.e., name = prefix-lkajsdla
        :return: (bool)
        """
        name_pattern = '{}-'.format(prefix)
        for pod in self._pods:
            if name_pattern in pod.get_name() and pod.get_namespace() == namespace:
                if pod.get_state() == PodStatus.RUNNING.value:
                    return True

        return False

    def is_pod_running(self,
                       namespace: str,
                       name: str) -> bool:
        """
        check whether pod is running or not
        :param namespace: (str) namespace
        :param name: (str) pod name
        :return: (bool)
        """
        for pod in self._pods:
            if name == pod.get_name() and pod.get_namespace() == namespace:
                if pod.get_state() == PodStatus.RUNNING.value:
                    return True

        return False

    def is_namespace_deployed(self,
                              namespace: str) -> bool:
        """
        check whether namespace is deployed or not
        :param namespace: (str)
        :return: (bool)
        """
        for item in self._namespaces:
            if item.get_name() == namespace:
                return True

        return False

    def get_pods(self) -> List[Pod]:
        """
        get pod list
        :return: (List[Pod])
        """
        return self._pods

    def set_pods(self, val: List[Pod]):
        """
        set pod list
        :param val: (List[Pod])
        :return:
        """
        if type(val) != list:
            raise TypeError('Invalid type. Must input List[Pod]')

        for item in val:
            if type(item) != Pod:
                raise TypeError('Invalid type. Must input List[Pod]')

        if self._pods:
            self._pods.clear()

        self._pods = val

    def get_pods_for_deployment(self,
                                namespace: str,
                                deployment: str) -> List[str]:
        """
        get pod name list for deployment
        :param namespace: (str)
        :param deployment: (str)
        :return: (list(str))
        """
        pods = []
        for item in self._pods:
            if namespace == item.get_namespace() and deployment+'-' in item.get_name():
                pods.append(item.get_name())

        return pods

    def get_number_of_pods(self, node_name: str) -> int:
        """
        get number of pods for node_name
        :param node_name: (str)
        :return:
        """
        number_of_pods = 0
        for pod in self._pods:
            if pod.get_node_name() == node_name:
                number_of_pods += 1

        return number_of_pods

    def get_pods_for_daemonset(self,
                               namespace: str,
                               deployment: str) -> List[str]:
        """
        get pod list for daemonset
        :param namespace: (str) namespace name
        :param deployment: (str) deployment name
        :return: (list[str]) pod name list
        """
        pods = []

        for item in self._pods:
            if namespace == item.get_namespace() and deployment + '-' in item.get_name():
                pods.append(item.get_name())

        return pods
