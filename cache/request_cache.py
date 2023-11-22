import time
import uuid

import threading
import datetime
from typing import List

from django.apps import apps
from gwlink_manager.settings import get_logger
from gwlink_manager import settings
from mqtt.model.common.type import RequestStatus
from mqtt.model.request import Request
from utils.dateformat import DateFormatter


class RequestCache:
    """
    class request cache (singleton instance)
    """
    # non error
    SUCCESS = 'no_error'
    NON_BLOCKING_MODE = 'Non blocking mode'
    REQUEST_TIMEOUT = 'Request timeout'
    # error
    REQUEST_NOT_CACHED = 'Request not cached'
    NOT_READY = 'Invalid request status(not_ready)'

    _max_request_wait_timeout = None
    _request_wait_check_tick = None

    _cleanup_thread = {}
    _request_expired_timeout = None
    _expired_requests_check_period = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()

        return cls._instance

    def _config(self):
        # set logger
        self._logger = get_logger(__name__)
        self.AgentRequestCache = apps.get_model('cache', 'AgentRequestCache')
        self._max_request_wait_timeout = settings.MAX_REQUEST_WAIT_TIMEOUT
        self._request_wait_check_tick = settings.REQUEST_WAIT_CHECK_TICK
        self._expired_requests_check_period = settings.EXPIRED_REQUESTS_CHECK_PERIOD
        self._request_expired_timeout = settings.REQUEST_EXPIRED_SECONDS

        # register cleanup thread for cached timeout request
        self._cleanup_thread['thread'] = \
            threading.Thread(target=self._cached_request_cleanup_scheduler,
                             args=(),
                             daemon=True)
        self._cleanup_thread['lock'] = threading.Lock()

    def start(self):
        if self._cleanup_thread['thread']:
            self._cleanup_thread['thread'].start()

    def wait_requests(self, requests: List[str], timeout: int):
        """
        wait requests until request_id list is completed
        :param requests: (List[str]) request ids
        :param timeout: (int) await seconds
        :return: (dict)
        """
        request_status = {}

        if type(requests) != list:
            raise ValueError('Invalid value for requests')

        if not requests:
            raise ValueError('Invalid value for requests')

        for request_id in requests:
            if type(request_id) != str:
                raise ValueError('Invalid value for requests')

        if timeout > self._max_request_wait_timeout:
            timeout = self._max_request_wait_timeout

        # check whether request_id is cached
        for request_id in requests:
            agent_request = self.get_request(request_id)

            if agent_request is None:
                err = 'Request {} is not cached'.format(request_id)
                self._logger.error(err)
                return False, None, RequestCache.REQUEST_NOT_CACHED

            elif agent_request.status == RequestStatus.NOT_READY.value:
                err = RequestCache.NOT_READY
                self._logger.error(err)
                return False, None, err

        # wait start time
        start = time.time()
        number_of_requests = len(requests)

        while True:
            # wait all requests
            for request_id in requests:
                # completed request
                if request_id in request_status.keys():
                    continue

                # get request status
                agent_request = self.get_request(request_id)
                elapsed = time.time() - start

                # check whether requests is timeout
                if agent_request.status == RequestStatus.RUNNING.value:
                    if timeout < 0:
                        if elapsed >= settings.MAX_REQUEST_WAIT_TIMEOUT:
                            request_status[request_id] = {
                                'success': True,
                                'result': RequestCache.REQUEST_TIMEOUT,
                                'error': ''
                            }
                    else:
                        if elapsed >= timeout:
                            request_status[request_id] = {
                                'success': True,
                                'result': RequestCache.REQUEST_TIMEOUT,
                                'error': ''
                            }
                else:
                    request_status[request_id] = {
                        'success': agent_request.success,
                        'result': agent_request.result,
                        'error': agent_request.error
                    }

            # check whether all requests are completed
            if len(request_status) == number_of_requests:
                return True, request_status, ''

            time.sleep(self._request_wait_check_tick)

    def wait(self, request_id: str, timeout: int):
        """
        wait until request_id is completed
        :param request_id: (str) request id
        :param timeout: (int) await seconds
        timeout = 0; non-blocking mode

        :return:
        (bool) ok; True - success, False - failure
        (stdout) result
        (stderr) error message
        """
        if type(request_id) != str:
            raise ValueError('Invalid value for request_id')

        if type(timeout) != int:
            raise ValueError('Invalid value for timeout')

        if timeout == 0:
            return True, None, RequestCache.NON_BLOCKING_MODE

        if timeout > self._max_request_wait_timeout:
            timeout = self._max_request_wait_timeout

        # wait start time
        start = time.time()

        while True:
            agent_request = self.get_request(request_id)

            if agent_request is None:
                err = 'Request {} is not cached'.format(request_id)
                self._logger.error(err)
                return False, None, RequestCache.REQUEST_NOT_CACHED

            elapsed = time.time() - start

            if agent_request.status == RequestStatus.RUNNING.value:
                if timeout < 0:
                    if elapsed >= settings.MAX_REQUEST_WAIT_TIMEOUT:
                        return True, None, RequestCache.REQUEST_TIMEOUT
                else:
                    if elapsed >= timeout:
                        return True, None, RequestCache.REQUEST_TIMEOUT

            elif agent_request.status == RequestStatus.NOT_READY.value:
                err = RequestCache.NOT_READY
                self._logger.error(err)
                return False, None, err

            else:
                return agent_request.success, agent_request.result, agent_request.error

            time.sleep(self._request_wait_check_tick)

    @classmethod
    def issue_request_id(cls):
        """
        get request id
        :return: (str) request id
        """
        return str(uuid.uuid4())

    def set_response(self, request_id: str, success: bool, error: str, result: str):
        """
        set response for request
        :param request_id: (str)
        :param success: (bool)
        :param error: (str)
        :param result: (str)
        :return:
        """
        if type(request_id) != str:
            raise ValueError('Invalid value for request_id')

        if type(success) != bool:
            raise ValueError('Invalid value for success')

        if error is not None and type(error) != str:
            raise ValueError('Invalid value for error')

        if result is not None and type(result) != str:
            raise ValueError('Invalid value for result')

        # update response
        request = self.get_request(request_id)

        if request is None:
            self._logger.warning('Not found request entry for request_id {}'.format(request_id))
            return

        if success:
            request.status = RequestStatus.SUCCEEDED.value
        else:
            request.status = RequestStatus.FAILED.value

        request.response_date = DateFormatter.current_datetime_object()
        request.success = success
        request.result = result
        request.error = error
        request.save()

        return

    def get_request(self, request_id: str):
        """
        get request entry for request_id
        :param request_id: (str)
        :return:
        """
        agent_requests = self.AgentRequestCache.objects.filter(request_id=request_id)

        if len(agent_requests) <= 0:
            return None

        return agent_requests[0]

    def push_request(self, request: Request):
        """
        push request to request cache
        :param request: (mqtt.model.request) request object
        :return:
        """
        # save request to cache
        agent_request_cache = self.AgentRequestCache()
        agent_request_cache.request_id = request.get_request_id()
        agent_request_cache.status = RequestStatus.RUNNING.value
        agent_request_cache.url = request.get_path()
        agent_request_cache.method = request.get_method()
        agent_request_cache.request_date = request.get_create_datetime()
        agent_request_cache.save()

    def delete_request(self, request_id):
        """
        pop request from request cache
        :param request_id: (str) request id
        :return:
        """
        request = self.get_request(request_id)

        if request is None:
            self._logger.debug('Not found request entry for request_id {}'.format(request_id))
            return

        request.delete()

    def get_expired_requests(self):
        """
        get expired requests
        :return:
        """
        if type(self._request_expired_timeout) != int:
            raise ValueError('Invalid value for expired_seconds')

        AgentRequestCache = apps.get_model('cache', 'AgentRequestCache')

        return AgentRequestCache.objects.filter(
            request_date__lte=DateFormatter.current_datetime_object()
                              - datetime.timedelta(seconds=self._request_expired_timeout))

    def _cached_request_cleanup_scheduler(self):
        """
        cleanup thread for cached request (gwlink_migration)
        :return:
        """
        self._logger.debug('[start] _scheduler_cached_request_cleanup()')

        while True:
            # check invalid cached requests
            expired_requests = self.get_expired_requests()

            if len(expired_requests) > 0:
                expired_requests.delete()

            # sleep thread
            time.sleep(self._expired_requests_check_period)