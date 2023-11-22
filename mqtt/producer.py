import json
import time

import pika

from cache.localhost import Configure
from gwlink_manager import settings
from cache.request_cache import RequestCache
from gwlink_manager.common.error import get_exception_traceback
from mqtt.model.request import Request


class Publisher:
    """
    Request publisher to CEdge-agent
    """
    _channel = None
    _url = None
    _port = None
    _id = None
    _password = None
    _vhost = None
    _credentials = None
    _connection = None
    _logger = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()

        return cls._instance

    def _config(self):
        self._url = Configure().get_host()
        self._port = Configure().get_amqp_port()
        self._vhost = Configure().get_amqp_vhost()
        self._id = Configure().get_amqp_id()
        self._password = Configure().get_amqp_pwd()
        self._logger = settings.get_logger(__name__)

    def start(self):
        self._logger.info('MQTT publisher started')
        self.connect()

    def reconnect(self):
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(self._url,
                                      self._port,
                                      self._vhost,
                                      self._credentials))

    def connect(self):
        """
        initialize MQTT connection for vhost
        :return:
        """
        self._credentials = pika.PlainCredentials(self._id, self._password)
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(self._url,
                                      self._port,
                                      self._vhost,
                                      self._credentials))

    def emit(self, queue: str, body: Request):
        """
        emit request
        :param queue:
        :param body: (Request)
        :return:
        """
        if type(body) != Request:
            raise TypeError('Invalid type for body({})'.format(body))

        data = json.dumps(body.to_dict()).encode()
        self.publish(queue, data)

        # push request to request cache
        RequestCache().push_request(body)

    def publish(self, queue: str, data: bytes):
        """
        publish message
        :param queue: (str)
        :param data:
        :return:
        """
        retry_count = 10

        for i in range(0, retry_count):
            try:
                channel = self._connection.channel()
                channel.basic_publish(exchange='',
                                      routing_key=queue,
                                      body=data)
                return
            except Exception as exc:
                self._logger.debug(get_exception_traceback(exc))
                self._logger.debug('Reconnect')
                self.reconnect()
                time.sleep(1)
                continue

        self._logger.error('Fail to issue data.')

    def close_connection(self):
        """
        close MQTT connection for vhost
        :return:
        """
        self._connection.close()
