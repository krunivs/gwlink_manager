import os
import sys

from gwlink_manager import settings
from utils.threads import ThreadUtil

logger = settings.get_logger(__name__)

class Configure:
    """
    localhost info.
    """
    host = None
    http_port = None
    amqp_port = None
    amqp_id = None
    amqp_pwd = None
    amqp_vhost = None
    agent_port = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()
        return cls._instance

    def _config(self):
        """
        configure localhost env
        :return:
        """
        argvs = sys.argv
        isRunServer = False
        http_url = None

        if 'GWLINK_MANAGER_HOST' not in os.environ:
            logger.error('Not found env variable, \'GWLINK_MANAGER_HOST\'')
            ThreadUtil.exit_process()

        if not os.environ['GWLINK_MANAGER_HOST']:
            logger.error('Not found env variable\'s value, \'GWLINK_MANAGER_HOST=\'')
            ThreadUtil.exit_process()

        self.host = os.environ['GWLINK_MANAGER_HOST']

        for i in range(0, len(argvs)):
            if argvs[i] == 'runserver':
                isRunServer = True
                http_url = argvs[i+1]
                break

        if not isRunServer:
            return

        if not http_url:
            logger.error('Invalid argvs, Not found server address')
            ThreadUtil.exit_process()

        items = http_url.split(':')

        if items[1]:
            self.http_port = int(items[1])
        else:
            self.http_port = 80

        self.amqp_port = settings.MQTT_PORT
        self.amqp_id = settings.MQTT_ID
        self.amqp_pwd = settings.MQTT_PWD
        self.amqp_vhost = settings.MQTT_VHOST
        self.agent_port = settings.GW_AGENT_PORT

        logger.info("GWLINK MANAGER Configuration. "
                    "    GWLINK_MANAGER_HOST={}\n"
                    "    HTTP_PORT={}\n"
                    "    MQTT_HOST={}\n"
                    "    MQTT_PORT={}\n"
                    "    MQTT_VHOST={}\n"
                    "    MQTT_ID={}\n"
                    "    MQTT_PWD={}\n"
                    "    AGENT_PORT={}\n"
                    .format(self.host, self.http_port, self.host, self.amqp_port, self.amqp_vhost,
                            self.amqp_id, self.amqp_pwd, self.agent_port))

    def get_host(self):
        """
        get host
        :return:
        (str) host
        """
        return self.host

    def get_http_port(self):
        """
        get http port
        :return:
        (int) http port
        """
        return self.http_port

    def get_amqp_port(self):
        """
        get AMQP port
        :return:
        (int) AMQP port
        """
        return self.amqp_port

    def get_amqp_id(self):
        """
        get AMQP ID
        :return:
        (str) AMQP ID
        """
        return  self.amqp_id

    def get_amqp_pwd(self):
        """
        get AMQP password
        :return:
        (str) AMQP password
        """
        return self.amqp_pwd

    def get_amqp_vhost(self):
        """
        get AMQP vHost
        :return:
        (str) AMQP vHost
        """
        return self.amqp_vhost

    def get_agent_port(self):
        """
        get gw_agent port
        :return:
        (str) gw_agent port
        """
        return self.agent_port
