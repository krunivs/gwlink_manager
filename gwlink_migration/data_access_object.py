import time
import uuid

from django.apps import apps
from typing import List

from django.db.models import Q

from gwlink_manager.common.error import get_exception_traceback
from gwlink_migration.common.type import MigrationSubTask, MigrationStatus
from utils.dateformat import DateFormatter


class MigrationDAO:
    @staticmethod
    def get_migration_request(migration_id: int) -> (bool, object, str):
        """
        get migration request for migration_id(MigrationRequest.id)
        :param migration_id: (int) migration id
        :return:
        (bool) True - success, False - fail
        (MigrationRequest)
        (str) error
        """
        MigrationRequest = apps.get_model('gwlink_migration', 'MigrationRequest')

        try:
            migration_request_objects = MigrationRequest.objects.filter(id=migration_id)
        except Exception as exc:
            return False, None, 'Failed in MigrationRequest.objects.filter(id=migration_id), ' \
                                'caused by '+ get_exception_traceback(exc)

        return True, migration_request_objects[0], None

    @staticmethod
    def find_migration_requests(source_cluster_name: str,
                                source_namespace: str,
                                source_pod: str,
                                target_cluster_name: str,
                                target_node_name: str) -> (bool, bool, str):
        """
        find migration requests
        :param source_cluster_name: (str) source cluster name
        :param source_namespace: (str) migrate namespace
        :param source_pod: (str) migrate pod
        :param target_cluster_name: (str) target cluster name
        :param target_node_name: (str) target node name
        :return:
        (bool) True - success, False - fail
        (bool) True - running, False - not exist
        (str) error
        """
        MigrationRequest = apps.get_model('gwlink_migration', 'MigrationRequest')

        try:
            migration_request_objects = MigrationRequest.objects.filter(
                source_cluster_name=source_cluster_name,
                source_namespace=source_namespace,
                source_pod=source_pod,
                target_cluster_name=target_cluster_name,
                target_node_name=target_node_name)
        except Exception as exc:
            return False, None, 'Failed in MigrationRequest.objects.filter(id=migration_id), ' \
                                'caused by '+ get_exception_traceback(exc)

        return True, migration_request_objects, None

    @staticmethod
    def get_scheduled_migration_requests() -> (bool, List[object], str):
        """
        get SCHEDULED migration requests
        :return:
        (bool) True - success, False - fail
        (List[MigrationRequest])
        (str) error
        """
        MigrationRequest = apps.get_model('gwlink_migration', 'MigrationRequest')

        try:
            requests = MigrationRequest.objects.filter(~Q(status=MigrationStatus.COMPLETED.value) &
                                                       ~Q(status=MigrationStatus.ERROR_EXITED.value))
        except Exception as exc:
            return False, None, 'Failed in MigrationRequest.objects.filter(status=status), ' \
                                'caused by ' + get_exception_traceback(exc)

        return True, requests, None

    @staticmethod
    def get_migration_requests(status: str = None) -> (bool, List[object], str):
        """
        get ISSUED migration requests
        :param status: (str) migration status(defined in MigrationStatus)
        :return:
        (bool) True - success, False - fail
        (List[MigrationRequest])
        (str) error
        """
        if status:
            if not MigrationStatus.validate(status):
                return False, None, 'Invalid status({})'.format(status)

        MigrationRequest = apps.get_model('gwlink_migration', 'MigrationRequest')

        if not status:
            try:
                requests = MigrationRequest.objects.all().order_by('-issued_date')
            except Exception as exc:
                return False, None, 'Failed in MigrationRequest.objects.all(), ' \
                                    'caused by ' + get_exception_traceback(exc)

            return True, requests, None

        try:
            requests = MigrationRequest.objects.filter(status=status)
        except Exception as exc:
            return False, None, 'Failed in MigrationRequest.objects.filter(status=status), ' \
                                'caused by ' + get_exception_traceback(exc)

        return True, requests, None

    @staticmethod
    def delete_migration_request(migration_id: int) -> (bool, str):
        """
        delete migration request
        :param migration_id:
        :return:
        (bool) True - success, False - fail
        (str) error
        """
        ok, migration_request_object, error = MigrationDAO.get_migration_request(migration_id)
        if not ok:
            return ok, error

        try:
            migration_request_object.delete()
        except Exception as exc:
            return False, 'Failed in MigrationRequest.delete(), caused by ' + get_exception_traceback(exc)

        return True, None

    @staticmethod
    def get_all_migration_subtasks(migration_request_object: object) -> (bool, List[object], str):
        """
        get all migration sub tasks
        :param migration_request_object: (MigrationRequest)
        :return:
        (bool) True - success, False - fail
        (List[MigrationTask])
        (str) error
        """
        MigrationTask = apps.get_model('gwlink_migration', 'MigrationTask')

        try:
            migration_task_objects = MigrationTask.objects.filter(
                migration_request=migration_request_object)
        except Exception as exc:
            return False, None, 'Failed in MigrationTask.objects.filter(migration_request=migration_request_object), ' \
                                'caused by ' + get_exception_traceback(exc)

        return True, migration_task_objects, None

    @staticmethod
    def get_migration_subtask_by_sequence(migration_request_object: object,
                                          sequence: int) -> (bool, List[object], str):
        """
        get migration subtask by sequence
        :param migration_request_object:
        :param sequence: (int) migration subtask sequence number
        :return:
        (bool) True - success, False - fail
        (List[MigrationTask])
        (str) error
        """
        MigrationTask = apps.get_model('gwlink_migration', 'MigrationTask')

        try:
            subtask_objects = MigrationTask.objects.filter(
                migration_request=migration_request_object, sequence=sequence)
        except Exception as exc:
            error = 'Failed in MigrationTask.objects.filter().update(), caused by ' + get_exception_traceback(exc)
            return False, None, error

        return True, subtask_objects, None

    @staticmethod
    def update_migration_subtask(migration_request_object: object,
                                 sequence: int,
                                 status: str,
                                 error: str = None,
                                 reason: str = None) -> (bool, str):
        """
        update migration
        :param migration_request_object: (MigrationRequest)
        :param sequence: (int) subtask sequence
        :param status: (str) defined in MigrationStatus
        :param error: (str) defined in MigrationError
        :param reason: (str) defined in MigrationError
        :return:
        (bool) True - success, False - fail
        (str) error
        """
        MigrationTask = apps.get_model('gwlink_migration', 'MigrationTask')

        last_subtask_seq = migration_request_object.last_subtask_seq
        number_of_subtask = migration_request_object.number_of_subtask

        # select MigrationTask object
        try:
            migration_task_objects = MigrationTask.objects.filter(
                migration_request=migration_request_object, sequence=sequence)
        except Exception as exc:
            error = 'Failed in MigrationTask.objects.filter(), caused by ' + get_exception_traceback(exc)
            return False, error

        if not migration_task_objects:
            error = 'Failed in MigrationTask.objects.filter(), caused by Not found migration task'
            return False, error

        migration_status = migration_request_object.status
        migration_start_date = migration_request_object.start_date
        migration_end_date = migration_request_object.end_date

        migration_task_object = migration_task_objects[0]
        subtask_start_date = migration_task_object.start_date
        subtask_end_date = migration_task_object.end_date
        retry_count = migration_task_object.retry

        if not error:
            error =  migration_task_object.error
        if not reason:
            reason = migration_task_object.reason

        if status == MigrationStatus.DONE.value:
            subtask_end_date = DateFormatter.timestamp_to_str(time.time())

            # If final task is completed,
            if last_subtask_seq == (number_of_subtask - 1):
                migration_status = MigrationStatus.COMPLETED.value
                migration_end_date = subtask_end_date
            else:
            # next task
                last_subtask_seq = sequence + 1

        elif status == MigrationStatus.ERROR_EXITED.value:
            subtask_end_date = DateFormatter.timestamp_to_str(time.time())
            migration_end_date = subtask_end_date
            migration_status = MigrationStatus.ERROR_EXITED.value

        elif status == MigrationStatus.RUNNING.value:
            subtask_start_date = DateFormatter.timestamp_to_str(time.time())

            # If first task is running,
            if last_subtask_seq == 0:
                migration_start_date = subtask_start_date
                migration_status = MigrationStatus.RUNNING.value

        elif status == MigrationStatus.PENDING.value:
            migration_status = MigrationStatus.PENDING.value
            retry_count += 1

        else:
            return False, 'Unknown migration status'

        # update migration task status to migration request
        try:
            migration_task_object.status = status
            migration_task_object.retry = retry_count
            migration_task_object.reason = reason
            migration_task_object.error = error
            migration_task_object.start_date = subtask_start_date
            migration_task_object.end_date = subtask_end_date
            migration_task_object.save()
        except Exception as exc:
            error = 'Failed in MigrationTask.objects.save(), caused by ' + get_exception_traceback(exc)
            return False, error

        # update migration status to migration request
        try:
            migration_request_object.last_subtask_seq = last_subtask_seq
            migration_request_object.status = migration_status
            migration_request_object.update_date = DateFormatter.timestamp_to_str(time.time())
            migration_request_object.start_date = migration_start_date
            migration_request_object.end_date = migration_end_date
            migration_request_object.save()
        except Exception as exc:
            error = 'Failed in MigrationRequest().update(), caused by ' + get_exception_traceback(exc)
            return False, error

        return True, None

    @staticmethod
    def create_migration(source_cluster_name: str,
                         source_cluster_role: str,
                         source_namespace: str,
                         source_pod: str,
                         target_cluster_name: str,
                         target_node_name: str,
                         delete_origin: bool = False) -> (bool, str):
        """
        create migration request
        :param source_cluster_name: (str) source cluster name
        :param source_cluster_role: (str) source cluster role
        :param source_namespace: (str) migrate namespace
        :param source_pod: (str) migrate pod
        :param target_cluster_name: (str) target cluster name
        :param target_node_name: (str) target node name
        :param delete_origin: (bool) wanna to delete origin pod?
        :return:
        (bool) True - success, False - fail
        (str) error
        """
        """ set migration request information """

        MigrationRequest = apps.get_model('gwlink_migration', 'MigrationRequest')
        migration_request = MigrationRequest()
        issued_ts_str = DateFormatter.timestamp_to_str(time.time())
        request_id = str(uuid.uuid4())
        migration_request.id = request_id
        migration_request.source_cluster_name = source_cluster_name
        migration_request.source_cluster_role = source_cluster_role
        migration_request.source_pod = source_pod
        migration_request.source_namespace = source_namespace
        migration_request.delete_origin = delete_origin
        migration_request.target_cluster_name = target_cluster_name
        migration_request.target_node_name = target_node_name
        migration_request.issued_date = issued_ts_str

        if delete_origin:
            migration_request.number_of_subtask = 5
        else:
            migration_request.number_of_subtask = 4

        try:
            migration_request.save()
        except Exception as exc:
            error = 'Failed in MigrationRequest.save(), caused by ' + get_exception_traceback(exc)
            return False, error

        """ set migration task for migration request """
        # create snapshot
        MigrationTask = apps.get_model('gwlink_migration', 'MigrationTask')

        migration_task = MigrationTask()
        migration_task.migration_request_id = request_id
        migration_task.sequence = 0
        migration_task.task = MigrationSubTask.CREATE_SNAPSHOT.value
        migration_task.issued_date = issued_ts_str

        try:
            migration_task.save()
        except Exception as exc:
            migration_request.delete()
            error = 'Failed in MigrationRequest.save(), caused by ' + get_exception_traceback(exc)
            return False, error

        # validate snapshot
        migration_task = MigrationTask()
        migration_task.migration_request_id = request_id
        migration_task.sequence = 1
        migration_task.task = MigrationSubTask.VALIDATE_SNAPSHOT.value
        migration_task.issued_date = issued_ts_str

        try:
            migration_task.save()
        except Exception as exc:
            migration_request.delete()
            error = 'Failed in MigrationTask.save(), caused by ' + get_exception_traceback(exc)
            return False, error

        # restore
        migration_task = MigrationTask()
        migration_task.migration_request_id = request_id
        migration_task.sequence = 2
        migration_task.task = MigrationSubTask.RESTORE.value
        migration_task.issued_date = issued_ts_str

        try:
            migration_task.save()
        except Exception as exc:
            migration_request.delete()
            error = 'Failed in MigrationTask.save(), caused by ' + get_exception_traceback(exc)
            return False, error

        # validate migration
        migration_task = MigrationTask()
        migration_task.migration_request_id = request_id
        migration_task.sequence = 3
        migration_task.task = MigrationSubTask.VALIDATE_MIGRATION.value
        migration_task.issued_date = issued_ts_str

        try:
            migration_task.save()
        except Exception as exc:
            migration_request.delete()
            error = 'Failed in MigrationTask.save(), caused by ' + get_exception_traceback(exc)
            return False, error

        if delete_origin:
            migration_task = MigrationTask()
            migration_task.migration_request_id = request_id
            migration_task.sequence = 4
            migration_task.task = MigrationSubTask.DELETE_ORIGIN.value
            migration_task.issued_date = issued_ts_str

            try:
                migration_task.save()
            except Exception as exc:
                error = 'Failed in MigrationTask.save(), caused by ' + get_exception_traceback(exc)
                return False, error

        return True, None

    @staticmethod
    def delete_migration(migration_id: str):
        """
        delete MigrationRequest, MigrationTask for migration_id
        :param migration_id: (str) migration id
        :return:
        """
        ok, migration_object, error = MigrationDAO.get_migration_request(migration_id)

        if not ok:
            return ok, error

        ok, migration_subtask_objects, error = MigrationDAO.get_all_migration_subtasks(migration_object)

        if not ok:
            return ok, error

        for migration_subtask_object in migration_subtask_objects:
            try:
                migration_subtask_object.delete()
            except Exception as exc:
                error = 'Failed in MigrationTask.delete(), caused by ' + get_exception_traceback(exc)
                return False, error

        try:
            migration_object.delete()
        except Exception as exc:
            error = 'Failed in MigrationRequest.delete(), caused by ' + get_exception_traceback(exc)
            return False, error

        return True, None

