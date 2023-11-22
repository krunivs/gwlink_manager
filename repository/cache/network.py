import gc
from typing import List

from gwlink_manager import settings

from repository.common.type import ConnectionStatus, MultiClusterRole
from repository.model.netstat.endpoint import EndpointNetwork
from repository.model.netstat.multi_cluster import MultiClusterNetwork
from repository.model.netstat.service import MultiClusterService, ServiceExport, ServiceImport

class NetworkStatusCache:
    """
    Network Status repository for caching center,
    cluster, multi-cluster network connection
    """
    _logger = None
    _mc_network = None
    _mc_network_service = None

    def __init__(self):
        self.clear()

    def clear(self):
        """
        clear entire cache
        :return:
        """
        self._mc_network = None
        self._mc_network_service = MultiClusterService()
        self._logger = settings.get_logger(__name__)

    def get_mc_network(self) -> MultiClusterNetwork:
        """
        get multi cluster status object
        :return: (MultiClusterNetwork) mc network status object
        """
        return self._mc_network

    def set_mc_network(self, obj: MultiClusterNetwork):
        """
        set multi cluster status
        :param obj: (MultiClusterNetwork)
        :return:
        """
        if obj is not None:
            if type(obj) == MultiClusterNetwork:
                if self._mc_network:
                    self._mc_network = None

                self._mc_network = obj

    def set_endpoint(self, endpoint: EndpointNetwork):
        """
        set endpoint
        :param endpoint:
        :return:
        """
        self._mc_network.set_endpoint(endpoint)

    def get_mc_network_name(self) -> str:
        """
        get mc network name
        :return: (str)
        """
        if self._mc_network is None:
            return None
        if self._mc_network.name is None:
            return None

        return self._mc_network.name

    def get_remote_mc_network_name(self) -> str:
        """
        get remote multi-cluster cluster_id
        :return: (str) cluster id
        """
        if not self._mc_network:
            return None

        endpoints = self._mc_network.get_endpoints()
        if len(endpoints) <= 0:
            return None

        for endpoint in endpoints:
            if endpoint.get_role() == MultiClusterRole.REMOTE.value:
                return endpoint.get_name()

        self._logger.error('Not exist remote endpoint in multi-cluster network.')

        return None

    def set_mc_network_broker_role(self, role: str):
        """
        set multi cluster status
        :param role: MultiClusterRole.LOCAL or ConnectionStatus.REMOTE
        :return:
        """
        if self._mc_network is None:
            return

        self._mc_network.set_broker_role(role)

    def get_mc_network_broker_role(self) -> str:
        """
        get multi cluster network role
        :return: (str) broker role
        """
        if self._mc_network is None:
            return MultiClusterRole.UNKNOWN.value

        return self._mc_network.get_broker_role()

    def set_mc_network_globalnet(self, enabled: bool):
        """
        set multi cluster globalnet enabled
        :param enabled: (bool) True - enabled, False - disabled
        :return:
        """
        self._mc_network.set_globalnet(enabled)

    def set_mc_network_global_cidr(self, val: str):
        """
        set multi cluster global cidr
        :param val: (str) global vpn(i.e., '244.0.0.0/8')
        :return:
        """
        self._mc_network.set_global_cidr(val)

    def set_mc_network_cable_driver(self, val: str):
        """
        set multi cluster global cidr
        :param val: (str) tunneling driver(i.e., 'wireguard' or 'libswan' or 'ipsec')
        :return:
        """
        self._mc_network.set_cable_driver(val)

    def synchronize_mc_network_endpoints(self, endpoints: List[EndpointNetwork]):
        """
        synchronize multi cluster endpoints
        :param endpoints: (list(EndpointNetwork))
        :return:
        """
        return self._mc_network.synchronize_endpoints(endpoints)

    def get_mc_network_connection_status(self) -> str:
        """
        get mc network connection status
        :return:
        (ConnectionStatus(Enum)) connection status
        """
        if self._mc_network is None:
            return ConnectionStatus.UNAVAILABLE.value

        endpoints = self._mc_network.get_remote_endpoints()
        if len(endpoints) <= 0:
            return ConnectionStatus.UNAVAILABLE.value

        return endpoints[0].get_status()

    def is_mc_network_connected(self) -> bool:
        """
        check whether multi-cluster network is connected each other
        :return:
        """
        if self._mc_network is None:
            return False

        endpoints = self._mc_network.get_remote_endpoints()
        if len(endpoints) <= 0:
            return False

        self._logger.debug('remote endpoints: {}'.format(len(endpoints)))

        if endpoints[0].get_status() == ConnectionStatus.CONNECTED.value:
            return True

        return False

    def get_mc_network_service(self) -> MultiClusterService:
        """
        get multi cluster service(exports, imports)
        :return:
        """
        return self._mc_network_service

    def synchronize_mc_network_service_exports(self, val: List[ServiceExport]):
        """
        synchronize multi cluster service exports
        :param val: (list(ServiceExport))
        :return:
        """
        return self._mc_network_service.synchronize_service_exports(val)

    def get_mc_network_service_exports(self) -> List[ServiceExport]:
        """
        get multi cluster service exports
        :return: (list(ServiceExport))
        """
        return self._mc_network_service.get_service_exports()

    def get_mc_network_service_imports(self) -> List[ServiceImport]:
        """
        get multi cluster service exports
        :return: (list(ServiceImport))
        """
        return self._mc_network_service.get_service_imports()

    def synchronize_mc_network_service_imports(self, val: List[ServiceImport]):
        """
        synchronize multi cluster service imports
        :param val: (list(ServiceImport)
        :return:
        """
        return self._mc_network_service.synchronize_service_imports(val)

    def is_service_exported(self, namespace: str, name: str) -> bool:
        """
        check whether service is exported or not
        :param namespace: (str) namespace
        :param name: (str) service name
        :return:
        """

        exports = self.get_mc_network_service_exports()
        for item in exports:
            if item.get_name() == name and item.get_namespace() == namespace:
                return True

        return False

    def is_service_imported(self, namespace: str, name: str) -> bool:
        """
        check whether service is imported or not
        :param namespace: (str) namespace
        :param name: (str) service name
        :return:
        """

        imports = self.get_mc_network_service_imports()
        for item in imports:
            if item.get_name() == name and item.get_namespace() == namespace:
                return True

        return False

    def get_imported_service(self, namespace: str, name: str) -> ServiceImport:
        """
        get imported service for namespace and name
        :param namespace: (str) namespace
        :param name: (str) name
        :return: (ServiceImport)
        """
        imports = self.get_mc_network_service_imports()
        for item in imports:
            if item.get_name() == name and item.get_namespace() == namespace:
                return item

        return None

