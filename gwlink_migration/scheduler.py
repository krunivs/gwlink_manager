import threading
import time

from cache.request_cache import RequestCache
from gwlink_manager import settings
from gwlink_migration.common.type import MigrationStatus, MigrationSubTask, MigrationError
from gwlink_migration.data_access_object import MigrationDAO
from mqtt.api import ClusterAgent
from repository.cache.cluster import ClusterCache
from repository.common.type import ClusterStatus
from utils.dateformat import DateFormatter


class MigrationScheduler:
    MIGRATION_TASK_TIMEOUT = 60*2
    MIGRATION_SCHEDULER = 'MIGRATION_SCHEDULER'

    _watch_threads = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._config()

        return cls._instance

    def _config(self):
        """
        configure NetworkWatcher
        :return:
        """
        self._logger = settings.get_logger(__name__)
        self._add_watch(MigrationScheduler.MIGRATION_SCHEDULER)

    def _add_watch(self, target):
        self._watch_threads[target] = {
            'thread': None,
            'target': target,
            'lock': threading.Lock(),
        }

    def start(self):
        """
        start network status watcher threads
        :return:
        """
        for _, value in self._watch_threads.items():
            if value['thread'] is None:
                value['thread'] = threading.Thread(target=self._watch_callback,
                                                   args=(value['target'],),
                                                   daemon=True)
                value['thread'].start()

    def create_snapshot(self,
                        migration_id: str,
                        source_cluster_name: str,
                        target_cluster_name: str,
                        source_cluster_role: str,
                        source_namespace: str,
                        source_pod: str) -> (bool, str, str):
        """
        create snapshot for namespaced pod
        :param migration_id: (str) migration ID
        :param source_cluster_name: (str) source cluster name
        :param target_cluster_name: (str) target cluster name
        :param source_cluster_role: (str) source cluster's role (defined in repository.common.type.MultiClusterRole)
        :param source_namespace: (str) source namespace
        :param source_pod: (str) source pod name
        :return:
        (bool) True - success, False - Fail
        (str) error
        (str) error reason
        """
        cache = ClusterCache().get_cluster(source_cluster_name)

        if not cache or cache['state'] != ClusterStatus.ACTIVE.value:
            return False, MigrationError.GW_AGENT_NOT_CONNECTED.value, None

        # request gw_agent to create snapshot
        request_id = ClusterAgent.create_snapshot(migration_id=migration_id,
                                                  source_cluster_name=source_cluster_name,
                                                  source_cluster_role=source_cluster_role,
                                                  target_cluster_name=target_cluster_name,
                                                  source_namespace=source_namespace,
                                                  source_pod=source_pod)

        # wait until agent's response arrive(timeout: MIGRATION_TASK_TIMEOUT)
        ok, stdout, stderr = RequestCache().wait(request_id, self.MIGRATION_TASK_TIMEOUT)

        if not ok:
            if stderr == RequestCache.NOT_READY or stderr == RequestCache.REQUEST_NOT_CACHED:
                error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
                self._logger.error(error)
                return False, MigrationError.GW_AGENT_REQUEST_DROPPED.value, None
            else:
                return False, stderr, None

        if stderr == RequestCache.REQUEST_TIMEOUT:
            return False, MigrationError.GW_AGENT_REQUEST_TIMEOUT.value, None

        return True, MigrationError.NONE.value, None

    def validate_snapshot(self,
                          migration_id: str,
                          source_cluster_name: str,
                          target_cluster_name: str,
                          source_cluster_role: str,
                          source_namespace: str,
                          source_pod: str) -> (bool, str, str):
        """
        validate snapshot for namespaced pod
        :param migration_id: (str) migration ID
        :param source_cluster_name: (str) source cluster name
        :param target_cluster_name: (str) target cluster name
        :param source_cluster_role: (str) source cluster's role (defined in repository.common.type.MultiClusterRole)
        :param source_namespace: (str) source namespace
        :param source_pod: (str) source pod name
        :return:
        (bool) True - success, False - Fail
        (str) error
        (str) error reason
        """
        cache = ClusterCache().get_cluster(source_cluster_name)

        if not cache or cache['state'] != ClusterStatus.ACTIVE.value:
            return False, MigrationError.GW_AGENT_NOT_CONNECTED.value, None

        # request gw_agent to validate snapshot
        request_id = ClusterAgent.validate_snapshot(migration_id=migration_id,
                                                    source_cluster_name=source_cluster_name,
                                                    source_cluster_role=source_cluster_role,
                                                    target_cluster_name=target_cluster_name,
                                                    source_namespace=source_namespace,
                                                    source_pod=source_pod)

        # wait until agent's response arrive(timeout: self.MIGRATION_TASK_TIMEOUT)
        ok, stdout, stderr = RequestCache().wait(request_id, self.MIGRATION_TASK_TIMEOUT)

        if not ok:
            if stderr == RequestCache.NOT_READY or stderr == RequestCache.REQUEST_NOT_CACHED:
                error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
                self._logger.error(error)
                return False, MigrationError.GW_AGENT_REQUEST_DROPPED.value, None
            else:
                return False, stderr, None

        if stderr == RequestCache.REQUEST_TIMEOUT:
            return False, MigrationError.GW_AGENT_REQUEST_TIMEOUT.value, None

        return True, MigrationError.NONE.value, None

    def restore_snapshot(self,
                         migration_id: str,
                         source_cluster_name: str,
                         source_cluster_role: str,
                         target_cluster_name: str,
                         target_node_name: str,
                         source_namespace: str,
                         source_pod:str) -> (bool, str, str):
        """
        restore namespaced pod snapshot in target cluster's node
        :param migration_id: (str) migration ID
        :param source_cluster_name: (str) source cluster name
        :param source_cluster_role: (str) source cluster role
        :param target_cluster_name: (str) target cluster name
        :param target_node_name: (str) target node in target cluster
        :param source_namespace: (str) source namespace
        :param source_pod: (str) source pod name
        :return:
        (bool) True - success, False - Fail
        (str) error
        (str) error reason
        """
        cache = ClusterCache().get_cluster(source_cluster_name)

        if not cache or cache['state'] != ClusterStatus.ACTIVE.value:
            return False, MigrationError.GW_AGENT_NOT_CONNECTED.value, None

        # request gw_agent to validate snapshot
        request_id = ClusterAgent.restore_snapshot(migration_id=migration_id,
                                                   source_cluster_name=source_cluster_name,
                                                   source_cluster_role=source_cluster_role,
                                                   target_cluster_name=target_cluster_name,
                                                   target_node_name=target_node_name,
                                                   source_namespace=source_namespace,
                                                   source_pod=source_pod)

        # wait until agent's response arrive(timeout: self.MIGRATION_TASK_TIMEOUT)
        ok, stdout, stderr = RequestCache().wait(request_id, self.MIGRATION_TASK_TIMEOUT)

        if not ok:
            if stderr == RequestCache.NOT_READY or stderr == RequestCache.REQUEST_NOT_CACHED:
                error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
                self._logger.error(error)
                return False, MigrationError.GW_AGENT_REQUEST_DROPPED.value, None
            else:
                return False, stderr, None

        if stderr == RequestCache.REQUEST_TIMEOUT:
            return False, MigrationError.GW_AGENT_REQUEST_TIMEOUT.value, None

        return True, MigrationError.NONE.value, None

    def validate_migration(self,
                           migration_id: str,
                           target_cluster_name: str,
                           target_node_name: str,
                           source_cluster_name: str,
                           source_cluster_role: str,
                           source_namespace: str,
                           source_pod: str) -> (bool, str, str):
        """
        validate namespaced pod snapshot in target cluster's node
        :param migration_id: (str) migration ID
        :param target_cluster_name: (str) target cluster name
        :param target_node_name: (str) target node in target cluster
        :param source_cluster_name: (str) source cluster name
        :param source_cluster_role: (str) source cluster role
        :param source_namespace: (str) source namespace
        :param source_pod: (str) source pod name
        :return:
        (bool) True - success, False - Fail
        (str) error
        (str) error reason
        """
        cache = ClusterCache().get_cluster(target_cluster_name)

        if not cache or cache['state'] != ClusterStatus.ACTIVE.value:
            return False, MigrationError.GW_AGENT_NOT_CONNECTED.value, None

        # request gw_agent to validate snapshot
        request_id = ClusterAgent.validate_restored_snapshot(migration_id=migration_id,
                                                             target_cluster_name=target_cluster_name,
                                                             target_node_name=target_node_name,
                                                             source_namespace=source_namespace,
                                                             source_cluster_name=source_cluster_name,
                                                             source_cluster_role=source_cluster_role,
                                                             source_pod=source_pod)

        # wait until agent's response arrive(timeout: self.MIGRATION_TASK_TIMEOUT)
        ok, stdout, stderr = RequestCache().wait(request_id, self.MIGRATION_TASK_TIMEOUT)

        if not ok:
            if stderr == RequestCache.NOT_READY or stderr == RequestCache.REQUEST_NOT_CACHED:
                error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
                self._logger.error(error)
                return False, MigrationError.GW_AGENT_REQUEST_DROPPED.value, None
            else:
                return False, stderr, None

        if stderr == RequestCache.REQUEST_TIMEOUT:
            return False, MigrationError.GW_AGENT_REQUEST_TIMEOUT.value, None

        return True, MigrationError.NONE.value, None

    def delete_origin(self,
                      migration_id: str,
                      source_cluster_name: str,
                      source_namespace: str,
                      source_pod: str) -> (bool, str, str):
        """
        delete origin pod
        :param migration_id: (str) migration ID
        :param source_cluster_name: (str) source cluster name
        :param source_namespace: (str) source namespace
        :param source_pod: (str) source pod name
        :return:
        (bool) True - success, False - Fail
        (str) error
        (str) error reason
        """
        cache = ClusterCache().get_cluster(source_cluster_name)

        if not cache or cache['state'] != ClusterStatus.ACTIVE.value:
            return False, MigrationError.GW_AGENT_NOT_CONNECTED.value, None

        # request gw_agent to validate snapshot
        request_id = ClusterAgent.delete_migration_source(migration_id=migration_id,
                                                          source_cluster_name=source_cluster_name,
                                                          source_namespace=source_namespace,
                                                          source_pod=source_pod)

        # wait until agent's response arrive(timeout: self.MIGRATION_TASK_TIMEOUT)
        ok, stdout, stderr = RequestCache().wait(request_id, self.MIGRATION_TASK_TIMEOUT)

        if not ok:
            if stderr == RequestCache.NOT_READY or stderr == RequestCache.REQUEST_NOT_CACHED:
                error = 'ReqeustCache not ready or request is not cached, caused by {}'.format(stderr)
                self._logger.error(error)
                return False, MigrationError.GW_AGENT_REQUEST_DROPPED.value, None
            else:
                return False, stderr, None

        if stderr == RequestCache.REQUEST_TIMEOUT:
            return False, MigrationError.GW_AGENT_REQUEST_TIMEOUT.value, None

        return True, MigrationError.NONE.value, None

    def execute_subtask(self, request: object, subtask: object) -> (bool, str, str):
        """
        execute subtask
        :param request: (MigrationRequest)
        :param subtask: (MigrationTask)
        :return:
        (bool) True - success, False - Fail
        (str) error
        (str) error reason
        """
        # MigrationRequest
        migration_id = request.id
        source_cluster_name = request.source_cluster_name
        source_cluster_role = request.source_cluster_role
        source_namespace = request.source_namespace
        source_pod = request.source_pod
        target_cluster_name = request.target_cluster_name
        target_node_name = request.target_node_name

        # MigrationTask
        task = subtask.task

        if task == MigrationSubTask.CREATE_SNAPSHOT.value:
            return self.create_snapshot(migration_id=migration_id,
                                        source_cluster_name=source_cluster_name,
                                        source_cluster_role=source_cluster_role,
                                        target_cluster_name=target_cluster_name,
                                        source_namespace=source_namespace,
                                        source_pod=source_pod)

        elif task == MigrationSubTask.VALIDATE_SNAPSHOT.value:
            return self.validate_snapshot(migration_id=migration_id,
                                          source_cluster_name=source_cluster_name,
                                          source_cluster_role=source_cluster_role,
                                          target_cluster_name=target_cluster_name,
                                          source_namespace=source_namespace,
                                          source_pod=source_pod)

        elif task == MigrationSubTask.RESTORE.value:
            return self.restore_snapshot(migration_id=migration_id,
                                         source_cluster_name=source_cluster_name,
                                         source_cluster_role=source_cluster_role,
                                         target_cluster_name=target_cluster_name,
                                         target_node_name=target_node_name,
                                         source_namespace=source_namespace,
                                         source_pod=source_pod)

        elif task == MigrationSubTask.VALIDATE_MIGRATION.value:
            return self.validate_migration(migration_id=migration_id,
                                           target_cluster_name=target_cluster_name,
                                           target_node_name=target_node_name,
                                           source_cluster_name=source_cluster_name,
                                           source_cluster_role=source_cluster_role,
                                           source_namespace=source_namespace,
                                           source_pod=source_pod)

        elif task == MigrationSubTask.DELETE_ORIGIN.value:
            return self.delete_origin(migration_id=migration_id,
                                      source_cluster_name=source_cluster_name,
                                      source_namespace=source_namespace,
                                      source_pod=source_pod)

        else:
            error = MigrationError.INVALID_SUBTASK.value
            reason = 'Invalid task value({}) in MigrateTask table'.format(task)
            self._logger.error(error)
            return False, error, reason


    def run_migration_subtask(self, request: object, subtask: object) -> (bool, str, str):
        """
        run migration subtask
        :param request: (MigrationRequest)
        :param subtask: (MigrationTask)
        :return:
        (bool) True - success, False - Fail
        (str) update status
        (str) error message
        """
        task = subtask.task

        # execute subtask
        ok, error, reason = self.execute_subtask(request, subtask)

        if ok:
            # If subtask exec is succeed, update status to DONE, and encounter last_subtask_seq
            return True, None, MigrationStatus.DONE.value

        if error in (MigrationError.SNAPSHOT_MANIFEST_DELETE_ERROR.value,
                     MigrationError.RESTORE_MANIFEST_DELETE_ERROR.value):
            self._logger.warning('Failed to delete livmigration resource')
            return True, None, MigrationStatus.DONE.value

        # fail to run do_subtask()
        # retryable error
        if error in (MigrationError.CONNECTION_REFUSED.value,
                     MigrationError.CONNECTION_RESET_BY_PEER.value,
                     MigrationError.NETWORK_UNREACHABLE.value,
                     MigrationError.GW_AGENT_NOT_CONNECTED.value,
                     MigrationError.GW_AGENT_REQUEST_TIMEOUT.value,
                     MigrationError.SHARED_DIRECTORY_NOT_READY.value,
                     MigrationError.SHARED_DIRECTORY_NOT_FOUND.value,
                     MigrationError.LIVMIGRATION_CRO_NOT_FOUND.value,
                     MigrationError.GW_AGENT_REQUEST_DROPPED.value):

            return False, error, MigrationStatus.PENDING.value

        # retryable error
        elif error == MigrationError.DESCRIPTION_FILE_NOT_FOUND.value:
            if task == MigrationSubTask.VALIDATE_SNAPSHOT.value:
                return False, error, MigrationStatus.PENDING.value

            else:
                return False, error, MigrationStatus.ERROR_EXITED.value

        # critical error: no retry
        else:
            return False, error, MigrationStatus.ERROR_EXITED.value

    def _watch_callback(self, target):
        """
        thread callback for watch request command, and execute it
        :return:
        """
        logger = self._logger
        logger.info('start MIGRATION_SCHEDULER')

        while True:
            # process ISSUED migration tasks
            ok, request_objects, error = MigrationDAO.get_scheduled_migration_requests()

            if not ok:
                logger.error(error)
                continue

            for request_object in request_objects:
                last_subtask_seq = request_object.last_subtask_seq
                issued_date = request_object.issued_date

                issued_date_ts = DateFormatter.to_timestamp(issued_date)
                current_ts = time.time()

                # check whether migration request is expired
                if current_ts - issued_date_ts > settings.MIGRATION_REQUEST_EXPIRATION_TIME:
                    ok, error = MigrationDAO.update_migration_subtask(
                        request_object, last_subtask_seq, MigrationStatus.PENDING.value,
                        MigrationError.MIGRATION_TIMEOUT_EXPIRED.value)

                    if not ok:
                        error_message = 'Failed in MigrationDAO.update_migration_subtask(), caused by ' + error
                        logger.error(error_message)
                        continue

                # get last subtask sequence
                ok, subtask_objects, error = \
                    MigrationDAO.get_migration_subtask_by_sequence(request_object, last_subtask_seq)

                if not ok:
                    error_message = 'Failed in MigrationDAO.get_migration_subtask_by_sequence({}, {}), ' \
                                    'caused by {}'.format(request_object, last_subtask_seq, error)
                    logger.error(error_message)

                    continue

                if not subtask_objects:
                    error_message = 'Failed in MigrationDAO.get_migration_subtask_by_sequence({}, {}), ' \
                                    'caused by Not found subtask'.format(request_object, last_subtask_seq)
                    logger.error(error_message)

                    continue

                # process subtask
                subtask_object = subtask_objects[0]
                subtask_status = subtask_object.status
                retry_count = subtask_object.retry

                if subtask_status == MigrationStatus.ISSUED.value:
                    # update status to RUNNING
                    ok, error = MigrationDAO.update_migration_subtask(
                        request_object, last_subtask_seq, MigrationStatus.RUNNING.value)

                    if not ok:
                        error_message = 'Failed in MigrationDAO.update_migration_subtask(), caused by ' + error
                        logger.error(error_message)

                        continue

                    # run migration subtask
                    ok, error, changing_subtask_status = self.run_migration_subtask(request_object, subtask_object)

                    # update failed status (PENDING | ERROR_EXITED)
                    if not ok:
                        reason = 'Failed in run_migration_subtask(), caused by ' + error
                        logger.error(reason)

                        ok, error = MigrationDAO.update_migration_subtask(
                            request_object, last_subtask_seq, changing_subtask_status, error, reason)

                        if not ok:
                            error_message = 'Failed in MigrationDAO.update_migration_subtask(), caused by ' + error
                            logger.error(error_message)

                        continue

                    # update success status
                    ok, error = MigrationDAO.update_migration_subtask(
                        request_object, last_subtask_seq, changing_subtask_status)

                    if not ok:
                        error_message = 'Failed in MigrationDAO.update_migration_subtask(), caused by ' + error
                        logger.error(error_message)

                        continue

                elif subtask_status == MigrationStatus.PENDING.value:
                    # check retry count whether it exceeds max retry bound
                    if retry_count > settings.MAX_MIGRATION_SUBTASK_RETRY:
                        ok, error = MigrationDAO.update_migration_subtask(
                            request_object, last_subtask_seq, MigrationStatus.ERROR_EXITED.value)

                        if not ok:
                            error_message = 'Failed in MigrationDAO.update_migration_subtask(), caused by ' + error
                            logger.error(error_message)

                        continue

                    # update status to RUNNING
                    ok, error = MigrationDAO.update_migration_subtask(
                        request_object, last_subtask_seq, MigrationStatus.RUNNING.value)

                    if not ok:
                        error_message = 'Failed in MigrationDAO.update_migration_subtask(), caused by ' + error
                        logger.error(error_message)

                        continue

                    # run migration subtask
                    ok, error, changing_subtask_status = self.run_migration_subtask(request_object, subtask_object)

                    # update failed status (PENDING | ERROR_EXITED)
                    if not ok:
                        reason = 'Failed in run_migration_subtask(), caused by ' + error
                        logger.error(reason)

                        ok, error = MigrationDAO.update_migration_subtask(
                            request_object, last_subtask_seq, changing_subtask_status, error, reason)

                        if not ok:
                            error_message = 'Failed in MigrationDAO.update_migration_subtask(), caused by ' + error
                            logger.error(error_message)

                        continue

                    # update success status
                    ok, error = MigrationDAO.update_migration_subtask(
                        request_object, last_subtask_seq, changing_subtask_status)

                    if not ok:
                        error_message = 'Failed in MigrationDAO.update_migration_subtask(), caused by ' + error
                        logger.error(error_message)

                        continue

                else:
                    # If subtask status is in RUNNING, ERROR_EXITED, DONE, UNKNOWN, ignore it.
                    continue

            time.sleep(1)
