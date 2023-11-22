import os
import threading

from cedge_agent import settings
from repository.common.type import MultiClusterRole
from utils.fileutils import FileUtil


class MultiClusterConfig:
    """
    Multi Cluster Configuration
    """
    _config_file = None
    fields = {
        '_enabled': 'bool',         # Is multi-cluster enabled?
        '_role': 'str',             # role: 'local' - join to broker, 'remote' - join to remote broker
        '_broker_updated': 'bool',  # Is broker-info.subm file updated?
    }
    _enabled = False
    _role = None
    _broker_updated = False
    _lock = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()

        return cls._instance

    def _config(self):
        self._config_file = settings.MULTI_CLUSTER_CONFIG_FILE

        if not os.path.isfile(self._config_file):
            raise FileNotFoundError('Not found {}'.format(self._config_file))

        config = FileUtil.from_json_file(self._config_file)
        if '_enabled' not in config:
            raise KeyError('Not found \'_enabled\' key in {} file'.format(self._config_file))
        if '_role' not in config:
            raise KeyError('Not found \'_role\' key in {} file'.format(self._config_file))
        if '_broker_updated' not in config:
            raise KeyError('Not found \'_broker_updated\' key in {} file'.format(self._config_file))

        self._enabled = config['_enabled']
        self._role = config['_role']
        self._broker_updated = config['_enabled']
        self._lock = threading.Lock()

    def reset_config(self):
        """
        reset multi-cluster config
        :return:
        """
        self._enabled = False
        self._role = MultiClusterRole.UNKNOWN.value
        self._broker_updated = False
        self._flush()

    def _flush(self):
        """
        flush config variables to file
        :return:
        """
        config = {
            '_enabled': self._enabled,
            '_role': self._role,
            '_broker_updated': self._broker_updated
        }
        self._lock.acquire()
        FileUtil.to_json_file(config, self._config_file)
        self._lock.release()

    def get_enabled(self):
        """
        get multi-cluster connection enabled
        :return: (bool)
        """
        return self._enabled

    def set_enabled(self, enabled : bool):
        """
        set multi-cluster connection enabled
        :param enabled: (bool)
        :return:
        """
        if type(enabled) != bool:
            raise ValueError('Invalid value type for enabled parameter')

        self._enabled = enabled
        self._flush()

    def get_role(self):
        """
        get cluster role in multi-cluster connection
        :return: (str) 'local' or 'remote'
        """
        return self._role

    def set_role(self, role: str):
        """
        set cluster role in multi-cluster connection
        :param role: (str) 'local' or 'remote'
        :return:
        """
        if not MultiClusterRole.validate(role):
            raise ValueError('Invalid parameter value')

        self._role = role
        self._flush()

    def get_broker_updated(self):
        """
        get broker updated in multi-cluster connection
        :return: (bool)
        """
        return self._broker_updated

    def set_broker_updated(self, broker_updated: bool):
        """
        set broker updated in multi-cluster connection
        :param broker_updated: (bool)
        :return:
        """
        if type(broker_updated) != bool:
            raise ValueError('Invalid value type for enabled parameter')

        self._broker_updated = broker_updated
        self._flush()
