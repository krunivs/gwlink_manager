import gc
import threading
import time

from gwlink_manager import settings
from repository.cache.components import ComponentCache
from repository.cache.metric import MetricCache
from repository.cache.network import NetworkStatusCache
from repository.cache.resources import ResourceCache
from repository.common.type import ClusterStatus
from repository.model.k8s.resource import ResourceBulk
from utils.dateformat import DateFormatter

logger = settings.get_logger(__name__)

class ClusterCache:
    """
    cluster cache
    """
    _cluster_session_audit = {}
    _cluster_session_alive_check_wait = 1
    _cluster_session_expired_timeout = 30

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()

        return cls._instance

    def _config(self):
        self._cluster = {}
        self._cluster_session_alive_check_wait = settings.CLUSTER_SESSION_CHECK_TICK
        self._cluster_session_expired_timeout = settings.CLUSTER_SESSION_EXPIRED_SECONDS

        self._cluster_session_audit['thread'] = \
            threading.Thread(target=self._cluster_session_audit_callback,
                             args=(),
                             daemon=True)

        self._cluster_session_audit['lock'] = threading.Lock()

    def _cluster_session_audit_callback(self):
        """
        cluster session check callback method
        :return:
        """
        logger.info("cluster session audit start.")

        while True:
            if self._cluster:
                delete_cluster_sessions = []

                # identify expired cluster sessions
                for cluster_name, attrs in self._cluster.items():
                    lastStateProbeTime = self._cluster[cluster_name]['lastStateProbeTime']

                    elapsed_seconds = DateFormatter.get_elapsed_seconds(lastStateProbeTime)

                    if not elapsed_seconds:
                        continue

                    if elapsed_seconds > self._cluster_session_expired_timeout:
                        delete_cluster_sessions.append(cluster_name)

                # delete expired cluster sessions
                for cluster_name in delete_cluster_sessions:
                    self.delete_cluster(cluster_name)
                    logger.info('cluster session [{}] is expired.'.format(cluster_name))

            time.sleep(self._cluster_session_alive_check_wait)

    def start(self):
        if self._cluster_session_audit['thread']:
            self._cluster_session_audit['thread'].start()
        else:
            logger.error('Fail to create thread')
            exit(1)

    def clear(self, cluster_name: str):
        """
        clear cluster session content
        :param cluster_name: (str) cluster name
        :return:
        """
        self._cluster[cluster_name] = {
            'state': ClusterStatus.ACTIVE.value,
            'lastStateProbeTime': None,  # '%Y-%m-%dT%H:%M:%SZ'
            'resource': ResourceCache(),
            'metric': MetricCache(),
            'network': NetworkStatusCache(),
            'component': ComponentCache(),
            'submariner_state': None,
        }

    def add_cluster(self, cluster_name: str):
        """
        add cluster session to cache
        :param cluster_name: (str) cluster name
        :return:
        """
        self.clear(cluster_name)

    def delete_cluster(self, cluster_name):
        """
        delete cluster session fro
        m cache
        :param cluster_name: (str) cluster name
        :return:
        """
        if cluster_name in self._cluster.keys():
            del self._cluster[cluster_name]

    def get_clusters(self) :
        """
        get all cluster sessions from cache
        :return:
        """
        return self._cluster

    def get_cluster(self, cluster_name):
        """
        get cluster session from cache
        :param cluster_name: (str) cluster name
        :return:
        """
        if cluster_name is None:
            return None

        if cluster_name in self._cluster.keys():
            return self._cluster[cluster_name]

        return None

    def initialize_cluster(self, cluster_name: str, val: ResourceBulk):
        """
        initialize cluster with resource bulk data
        :param cluster_name: (str)
        :param val: (ResourceBulk)
        :return:
        """
        cache = self.get_cluster(cluster_name)

        cache['resource'].set_nodes(val.get_nodes())
        cache['resource'].set_namespaces(val.get_namespaces())
        cache['resource'].set_pods(val.get_pods())
        cache['resource'].set_daemonsets(val.get_daemonsets())
        cache['resource'].set_deployments(val.get_deployments())
        cache['resource'].set_services(val.get_services())
        cache['state'] = ClusterStatus.ACTIVE.value
