import uuid
from typing import List
from gwlink_manager.common.error import get_exception_traceback
from cluster.models import Cluster
from utils.dateformat import DateFormatter
from gwlink_manager import settings

class ClusterDAO:
    @staticmethod
    def get_all_cluster_id_and_name() -> (bool, List[Cluster], str):
        """
        get all cluster id and name object
        :return:
        (bool) True - success, False - fail
        (str) error message
        (list[cluster.models.Cluster]) Cluster objects
        """
        error_message = None

        try:
            cluster_objects = \
                Cluster.objects.all(). \
                    values('cluster_id',
                           'cluster_name')
        except Exception as exc:
            error_message = get_exception_traceback(exc)
            return False, None, error_message

        return True, cluster_objects, error_message

    @staticmethod
    def get_all_cluster_objects() -> (bool, List[Cluster], str):
        """
        get all cluster database objects
        :return:
        (bool) True - success, False - fail
        (list[cluster.models.Cluster]) Cluster objects
        (str) error message
        """
        error_message = None
        cluster_objects = []

        try:
            cluster_objects = \
                Cluster.objects.all(). \
                    values('cluster_id',
                           'cluster_name',
                           'description',
                           'registration_command',
                           'mc_connect_id',
                           'role',
                           'mc_config_state',
                           'broker_info',
                           'broker_info_update_date',
                           'create_date',
                           'update_date')
        except Exception as exc:
            error_message = get_exception_traceback(exc)
            return False, cluster_objects, error_message

        return True, cluster_objects, error_message

    @staticmethod
    def get_cluster_objects_by_name(cluster_name: str) -> (bool, List[Cluster], str):
        """
        get cluster database objects by cluster name
        :param cluster_name: (str) cluster name
        :return:
        (bool) True - success, False - fail
        (list[cluster.models.Cluster]) Cluster objects
        (str) error message
        """
        error_message = None
        cluster_objects = []

        # retrieve cluster data from database
        if cluster_name:
            try:
                cluster_objects = \
                    Cluster.objects.filter(cluster_name=cluster_name). \
                        values('cluster_id',
                               'cluster_name',
                               'description',
                               'registration_command',
                               'mc_connect_id',
                               'role',
                               'mc_config_state',
                               'broker_info',
                               'broker_info_update_date',
                               'create_date',
                               'update_date')

            except Exception as exc:
                error_message = get_exception_traceback(exc)
                return False, cluster_objects, error_message

        return True, cluster_objects, error_message

    @staticmethod
    def register_cluster_object(cluster_name: str,
                                description) -> (bool, List[Cluster], str):
        """
        register cluster object
        :param cluster_name: (str) cluster name
        :param description: (str) cluster's description
        :return:
        (bool) True - success, False - fail
        (list[cluster.models.Cluster]) Cluster objects
        (str) error message
        """
        error_message = None

        try:
            cluster = Cluster()
            cluster.cluster_id = str(uuid.uuid4())
            cluster.cluster_name = cluster_name
            cluster.description = description
            cluster.registration_command = None
            cluster.save()
        except Exception as exc:
            error_message = get_exception_traceback(exc)
            return False, None, error_message

        return True, cluster, error_message

    @staticmethod
    def get_cluster_id(cluster_name: str) -> (bool, List[Cluster], str):
        """
        get cluster id by cluster name
        :param cluster_name: (str) unique
        :return:
        (bool) True - success, False - fail
        (list[cluster.models.Cluster]) Cluster objects
        (str) error message
        """
        error_message = 'no_error'

        try:
            cluster_objects = \
                Cluster.objects.filter(cluster_name=cluster_name). \
                    values('cluster_id')
        except Exception as exc:
            error_message = get_exception_traceback(exc)
            return False, None, error_message

        if len(cluster_objects) <= 0:
            return True, None, error_message

        return True, cluster_objects[0].get('cluster_id', None), error_message

    @staticmethod
    def get_cluster_objects_by_connected_id(mc_connect_id: str) -> (bool, List[Cluster], str):
        """
        get cluster objects by connected_id
        :param mc_connect_id: (str) multi-cluster connect id
        :return:
        (bool) True - success, False - fail
        (list[cluster.models.Cluster]) Cluster objects
        (str) error message
        """
        cluster_objects = []
        error_message = 'no_error'

        # retrieve cluster data from database
        if mc_connect_id:
            try:
                cluster_objects = \
                    Cluster.objects.filter(mc_connect_id=mc_connect_id). \
                        values('cluster_id',
                               'cluster_name',
                               'description',
                               'registration_command',
                               'mc_connect_id',
                               'role',
                               'mc_config_state',
                               'broker_info',
                               'broker_info_update_date',
                               'create_date',
                               'update_date')
            except Exception as exc:
                error_message = get_exception_traceback(exc)
                return False, cluster_objects, error_message

        return True, cluster_objects, error_message

    @staticmethod
    def get_cluster_broker_info(cluster_name: str) -> (bool, str, str):
        """
        get cluster broker_info by cluster name
        :param cluster_name: (str) unique
        :return:
        (bool) True - success, False - fail
        (str) broker info content
        (str) error message
        """
        error_message = 'no_error'

        try:
            cluster_objects = \
                Cluster.objects.filter(cluster_name=cluster_name). \
                    values('broker_info')

        except Exception as exc:
            error_message = get_exception_traceback(exc)
            return False, None, error_message

        if len(cluster_objects) <= 0:
            return True, None, error_message

        return True, cluster_objects[0].get('broker_info', None), error_message

    @staticmethod
    def update_cluster_broker_info(cluster_name: str, broker_info_content: str) -> (bool, str, str):
        """
        update cluster broker_info by cluster name
        :param cluster_name: (str) unique
        :param broker_info_content: (str) broker info content
        :return:
        (bool) True - success, False - fail
        (str) error message
        """
        try:
            Cluster.objects.filter(cluster_name=cluster_name). \
                update(broker_info=broker_info_content,
                       broker_info_update_date=DateFormatter.current_datetime_object())

        except Exception as exc:
            error_message = get_exception_traceback(exc)
            return False, error_message

        return True, None

    @staticmethod
    def update_multi_cluster_connection(cluster_name: str,
                                        mc_connect_id: str,
                                        role: str,
                                        mc_config_state: str,
                                        broker_info) -> (bool, str):
        """
        update cluster broker info
        :param cluster_name: (str) unique
        :param role: (str) cluster role
        :param mc_connect_id: (str) mc_connect_id
        :param mc_config_state: (str)
        :param broker_info: (str) broker info connecting
        :return:
        (bool): success
        (str): error
        """
        error_message = None

        try:
            Cluster.objects.filter(cluster_name=cluster_name). \
                update(mc_connect_id=mc_connect_id,
                       role=role,
                       mc_config_state=mc_config_state,
                       broker_info=broker_info,
                       broker_info_update_date=DateFormatter.current_datetime_object())
        except Exception as exc:
            error_message = get_exception_traceback(exc)
            return False, error_message

        return True, error_message

    @staticmethod
    def update_multi_cluster_config_state(cluster_name: str,
                                          mc_config_state: str) -> (bool, str):
        """
        update cluster broker info
        :param cluster_name: (str) unique
        :param mc_config_state: (str)
        :return:
        (bool): success
        (str): error
        """
        error_message = None

        try:
            Cluster.objects.filter(cluster_name=cluster_name). \
                update(mc_config_state=mc_config_state,
                       broker_info_update_date=DateFormatter.current_datetime_object())
        except Exception as exc:
            error_message = get_exception_traceback(exc)
            return False, error_message

        return True, error_message

    @staticmethod
    def get_mc_connect_id(cluster_name: str) -> (bool, str, str):
        """
        retrieve connect_id with cluster_name
        :param cluster_name: (str) cluster name
        :return:
        """
        error_message = None

        try:
            cluster_objects = Cluster.objects.filter(cluster_name=cluster_name).values('mc_connect_id')
        except Exception as exc:
            error_message = get_exception_traceback(exc)
            return False, None, error_message

        if len(cluster_objects) <= 0:
            return True, None, error_message

        return True, cluster_objects[0].get('mc_connect_id', None), error_message


    @staticmethod
    def delete_cluster(cluster_name: str) -> (bool, str):
        """
        delete cluster by name
        :param cluster_name: (str) cluster name
        :return: (bool, str); (success, error_message)
        """
        error_message = None

        try:
            cluster_objects = \
                Cluster.objects.filter(cluster_name=cluster_name)
        except Exception as exc:
            error_message = get_exception_traceback(exc)
            return False, error_message

        if cluster_objects:
            try:
                cluster_objects.delete()
            except Exception as exc:
                error_message = get_exception_traceback(exc)
                return False, error_message

        return True, error_message
