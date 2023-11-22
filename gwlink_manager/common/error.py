import inspect
import time
import yaml
from kubernetes import config
import traceback
from gwlink_manager.settings import get_logger

logger = get_logger(__name__)

from gwlink_manager.common.type import ErrorType
from utils.dateformat import DateFormatter

class GSLinkManagerError:
    INTERNAL_SERVER_ERROR = 'Internal server error'
    BAD_REQUEST_ERROR = 'Bad request'
    FILE_NOT_FOUND_ERROR = 'File not found'
    QUERY_PARAM_NOT_FOUND_ERROR = 'Query parameter key not found, query param={param}'
    BODY_NOT_FOUND_ERROR = 'Http body fields not found'
    BODY_FIELD_NOT_FOUND_ERROR = 'Http body field not found, body, field={field}'
    INVALID_QUERY_PARAM_VALUE = 'Invalid query param value, {param}={val}'
    INVALID_BODY_FIELD_VALUE = 'Invalid http body field value, {field}={val}'

    INVALID_CLUSTER_NAME_ERROR = 'Invalid cluster name, cluster={cluster}'
    CLUSTER_NOT_FOUND_ERROR = 'Cluster not found, cluster={cluster}'
    ENDPOINT_NOT_FOUND_ERROR = 'Endpoint not found, cluster={cluster}'
    CLUSTER_ID_NOT_FOUND_ERROR = 'Cluster ID not found, cluster={cluster}'
    CLUSTER_NOT_CONNECTED_ERROR = 'Cluster not connected, cluster={cluster}'
    LOCAL_CLUSTER_BROKER_NOT_READY_ERROR = 'Local cluster broker not ready, cluster={cluster}'
    REMOTE_CLUSTER_BROKER_NOT_READY_ERROR = 'Remote cluster broker not ready, cluster={cluster}'

    NOT_CONNECTED_MC_NETWORK = 'Not connected multi-cluster network, cluster={cluster}'
    NODE_NOT_FOUND_ERROR = 'Node not found, cluster={cluster}, node={node}'
    NODE_EXCEED_POD_CAPACITY_ERROR = 'Node exceed pod capacity, node={node}'
    NAMESPACE_NOT_FOUND_ERROR = 'Namespace not found, namespace={namespace}'
    POD_NOT_FOUND_ERROR = 'Pod not found, cluster={cluster}, pod={pod}, namespace={namespace}'
    POD_ALREADY_EXIST_ERROR = 'Pod, namespace is already existed in cluster, pod={pod}, namespace={namespace}, cluster={cluster}'
    DEPLOYMENT_NOT_FOUND_ERROR = 'Deployment not found, deployment={deployment}'
    DAEMONSET_NOT_FOUND_ERROR = 'Daemonset not found, daemonset={daemonset}'
    SERVICE_NOT_FOUND_ERROR = 'Service not found, service={service}'

    BROKER_INFO_REQUEST_TIMEOUT = 'Broker access information request timeout, cluster={cluster}'
    BROKER_STATUS_REQUEST_TIMEOUT = 'Broker status request timeout, cluster={cluster}'
    MULTI_CLUSTER_CONNECT_FAIL = 'Multi cluster connect fail, cluster={cluster}, reason={reason}'
    MULTI_CLUSTER_CONNECT_REQUEST_TIMEOUT = 'Multi cluster connect request timeout, cluster={cluster}'
    MULTI_CLUSTER_NETWORK_ALREADY_CONNECTED = 'Multi-cluster network is already connected, cluster={cluster}'
    MULTI_CLUSTER_DISCONNECT_REFUSED = 'Multi-cluster disconnect control is refused, cluster={cluster}, ' \
                                       'mc_config_state = {state}'
    MULTI_CLUSTER_NETWORK_ID_NOT_FOUND = 'Multi-cluster network id not found for cluster, cluster={cluster}'
    MULTI_CLUSTER_CONNECTED_REMOTE_CLUSTER_NOT_FOUND = 'Multi-cluster connected remote cluster not found, cluster={cluster}'
    MULTI_CLUSTER_NETWORK_UNAVAILABLE = 'Multi-cluster network connection unavailable, cluster={cluster}'
    SERVICE_NOT_EXPORTED = 'Service is not exported'

    MIGRATION_ALREADY_EXIST = 'Migration is already existed, src_cls={cluster1}, dst_cls={cluster2}, dst_node={node}, pod={pod}, ns={namespace}'
    MIGRATION_NOT_EXIST = 'Migration is not existed, migration_id={migration_id}'
    MIGRATION_IN_PROGRESS = 'Migration is in progress, migration_id={migration_id}'

    INVALID_MULTI_CLUSTER_NETWORK = 'Invalid multi-cluster network id among {cluster1}, {cluster2}'


class SystemInternalError(Exception):
    """
    user-defined exceptions: System internal Error
    object initial arguments
    arg0: (ErrorType) error_type: user defined common type
    arg1: (str) desc: description
    """

    def __init__(self, error_type, desc):
        self.error_type = error_type
        self.desc = desc

    def get_error_type(self):
        return self.error_type


class APIError(Exception):
    """
    user-defined exceptions: API Error
    object initial arguments
    arg0: (ErrorType) error_type: user defined common type
    arg1: (str) desc: description
    """

    def __init__(self, error_type, desc):
        self.error_type = error_type
        self.desc = desc

    def get_error_type(self):
        return self.error_type

def get_method_name():
    return inspect.stack()[1][3]

def get_exception_traceback(exception):
    """
    get exception traceback
    :param exception: (Exception)
    :return: (str) error traceback
    """
    exception_traceback = traceback.TracebackException.from_exception(exception)
    return ''.join(exception_traceback.format())

class ErrorHandler(Exception):
    """
    AppErrorHandler class
    desc: write common time and redefine common types, provide printing common log, json formatted common by user-level
    """
    DEBUG_MODE = 0x01
    DEPLOY_MODE = 0x02

    def __init__(self, exception):
        self.mode = ErrorHandler.DEBUG_MODE
        self.error = exception
        exception_traceback = traceback.TracebackException.from_exception(exception)
        self.str_traceback = ''.join(exception_traceback.format())
        self.logger = logger
        self.desc = None
        self.error_type = None
        self.time = time.time()
        self._set_error_desc(exception)
        self._set_error_type(exception)
        self._print_error_log()

    def _print_error_log(self):
        """
        desc: print common(Exception) log to app logger channel
        :return:
        """
        str_error = \
            '{0}{1} caused by {2}'.format(
                self.str_traceback,
                self.error_type.value['text'],
                self.desc)

        self.logger.error(str_error)

    def _set_error_desc(self, exception):
        """
        desc: set common argument from Exception raised
        :param exception:
        :return:
        """
        if type(exception) is APIError:
            self.desc = exception.desc
        elif type(exception) is SystemInternalError:
            self.desc = exception.desc
        else:
            if len(exception.args) > 0:
                self.desc = exception.args[0]

    def get_error_type(self):
        return self.error_type

    @staticmethod
    def no_error():
        """
        desc: returns json formatted 'no common'
        :return:
        """
        return {'time': DateFormatter.current_datetime(),
                'code': ErrorType.NO_ERROR.value['code'],
                'text': ErrorType.NO_ERROR.value['text'],
                'trace': None,
                'desc': None}

    def get_api_error(self):
        """
        desc: returns json formatted api-level common which filtered by api-level
        :return:
        """
        if self.mode == ErrorHandler.DEBUG_MODE:
            return {'time': self.time,
                    'code': self.error_type.value['code'],
                    'text': self.error_type.value['text'],
                    'desc': self.desc,
                    'trace': self.str_traceback}
        else:
            if type(self.error) is APIError:
                return {'time': self.time,
                        'code': self.error_type.value['code'],
                        'text': self.error_type.value['text'],
                        'desc': self.desc}
            else:  # provide abstract message caused by security reason
                return {'time': self.time,
                        'code': self.error_type.value['code'],
                        'text': 'system internal common',
                        'desc': 'contact admin with common code and time'}

    def get_system_error(self):
        """
        desc: returns json formatted system-level common which no filtered with traceback information
        :return:
        """
        return {'time': self.time,
                'code': self.error_type.value['code'],
                'text': self.error_type.value['text'],
                'desc': self.desc,
                'trace': self.str_traceback}

    def _set_error_type(self, exception):
        """
        desc: set common types from ErrorType enum class
        :param exception:
        :return:
        """
        if type(exception) is yaml.YAMLError:
            self.error_type = ErrorType.YAML_IO_ERROR
        elif type(exception) is yaml.MarkedYAMLError:
            self.error_type = ErrorType.YAML_SYNTAX_ERROR
        elif type(exception) is IOError:
            self.error_type = ErrorType.IO_ERROR
        elif type(exception) is RuntimeError:
            self.error_type = ErrorType.RUNTIME_ERROR
        elif type(exception) is NameError:
            self.error_type = ErrorType.NAME_ERROR
        elif type(exception) is TypeError:
            self.error_type = ErrorType.TYPE_ERROR
        elif type(exception) is ValueError:
            self.error_type = ErrorType.VALUE_ERROR
        elif type(exception) is OSError:
            self.error_type = ErrorType.OS_ERROR
        elif type(exception) is LookupError:
            self.error_type = ErrorType.LOOKUP_ERROR
        elif type(exception) is KeyError:
            self.error_type = ErrorType.KEY_ERROR
        elif type(exception) is BufferError:
            self.error_type = ErrorType.BUFFER_ERROR
        elif type(exception) is ArithmeticError:
            self.error_type = ErrorType.ARITHMETIC_ERROR
        elif type(exception) is ZeroDivisionError:
            self.error_type = ErrorType.ZERO_DIVISION_ERROR
        elif type(exception) is FloatingPointError:
            self.error_type = ErrorType.ZERO_DIVISION_ERROR
        elif type(exception) is OverflowError:
            self.error_type = ErrorType.OP_OVERFLOW_ERROR
        elif type(exception) is EOFError:
            self.error_type = ErrorType.EOF_ERROR
        elif type(exception) is IndexError:
            self.error_type = ErrorType.INDEX_ERROR
        elif type(exception) is MemoryError:
            self.error_type = ErrorType.MEMORY_ERROR
        elif type(exception) is RecursionError:
            self.error_type = ErrorType.RECURSIVE_ERROR
        elif type(exception) is BrokenPipeError:
            self.error_type = ErrorType.BROKEN_PIPE_ERROR
        elif type(exception) is ConnectionAbortedError:
            self.error_type = ErrorType.CONNECTION_ABORT_ERROR
        elif type(exception) is ConnectionError:
            self.error_type = ErrorType.CONNECTION_ERROR
        elif type(exception) is ConnectionRefusedError:
            self.error_type = ErrorType.CONNECTION_REFUSED_ERROR
        elif type(exception) is ConnectionResetError:
            self.error_type = ErrorType.CONNECTION_RESET_ERROR
        elif type(exception) is FileExistsError:
            self.error_type = ErrorType.FILE_EXIST_ERROR
        elif type(exception) is FileNotFoundError:
            self.error_type = ErrorType.FILE_NOT_FOUND_ERROR
        elif type(exception) is IsADirectoryError:
            self.error_type = ErrorType.DIRECTORY_REMOVE_ERROR
        elif type(exception) is NotADirectoryError:
            self.error_type = ErrorType.INVALID_DIRECTORY_CMD_ERROR
        elif type(exception) is PermissionError:
            self.error_type = ErrorType.PERMISSION_ERROR
        elif type(exception) is ProcessLookupError:
            self.error_type = ErrorType.PROCESS_NOT_FOUND_ERROR
        elif type(exception) is TimeoutError:
            self.error_type = ErrorType.TIMEOUT_ERROR
        elif type(exception) is AttributeError:
            self.error_type = ErrorType.INVALID_FILE_ATTRIBUTE_ERROR
        elif type(exception) is config.config_exception.ConfigException:
            self.error_type = ErrorType.K8S_CONFIG_ERROR
        elif type(exception) is APIError:
            self.error_type = exception.get_error_type()
        elif type(exception) is SystemInternalError:
            self.error_type = exception.get_error_type()
        else:
            self.error_type = ErrorType.UNKNOWN_ERROR
