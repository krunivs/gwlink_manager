class WorkloadViewModel:
    @staticmethod
    def get_condition_view_model() -> dict:
        """
        get resource condition view model
        :return: (dict)
        """
        return {
            "condition": None,  # (str) condition
            "status": None,  # (str) 'true' or 'false'
            "message": None,  # (str) error message
            "updated": None,  # (str) update datetime(yyyy-MM-dd HH:mm:SS)
        }

    @staticmethod
    def get_namespace_view_model() -> dict:
        """
        get namespace view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) namespace name
            "state": None,  # (str) namespace state("Active" or "NotReady" or "Terminating")
            "conditions": [],  # (list[condition_view_model from get_condition_view_model()]) namespace conditions
            "stime": None,  # (str) update datetime(yyyy-MM-dd HH:mm:SS)
            "age": None  # (str)
        }

    @staticmethod
    def get_all_namespace_view_model() -> dict:
        """
        get all namespace view model
        :return:
        """
        return {
            "name": None, # (str) cluster name
            "namespaces": [] # list(str) namespace list
        }

    @staticmethod
    def get_all_namespace_list_view_model() -> dict:
        """
        get all namespace view list model
        :return: (dict)
        """
        return {
            "name": None,  # (str) cluster name
            "id": None,  # (str) cluster id
            "clusters": []  # (list[namespace_view_model from get_namespace_view_model()])
        }

    @staticmethod
    def get_namespace_list_view_model() -> dict:
        """
        get namespace view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) cluster name
            "id": None,  # (str) cluster id
            "namespaces": []  # (list[namespace_view_model from get_namespace_view_model()])
        }

    @staticmethod
    def get_namespace_delete_view_model() -> dict:
        """
        get namespace delete view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) cluster name
            "id": None,  # (str) cluster id
            "namespace": None,  # deleted namespace
            "result": {
                "success": False,  # (bool) is success?
                "stdout": None,  # (str) stdout message
                "error": None  # (str)
            }
        }

    @staticmethod
    def get_pod_view_model() -> dict:
        """
        get pod view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) pod name
            "state": None,  # (str) pod state("Running" or "Pending" or "Succeeded" or "Failed")
            "namespace": None,  # (str) namespace name
            "labels": [],  # (list[str]) labels
            "host_ip": None,  # (str) node ip
            "node": None,  # (str) node hostname
            "pod_ip": None,  # (str) pod ip
            "conditions": [],  # (list[condition_view_model from get_condition_view_model()]) pod conditions
            "images": [],  # (list[str]) docker image list
            "stime": None,  # (str) pod start datetime
            "age": None
        }

    @staticmethod
    def get_pod_list_view_model() -> dict:
        """
        get pod list view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) cluster name
            "id": None,  # (str) cluster id
            "pods": []  # (list[pod_view_model from get_pod_view_model()])
        }

    @staticmethod
    def get_pod_deletion_view_model() -> dict:
        """
         get pod deletion view model
         :return: (dict)
         """
        return {
            "id": None,  # (str) cluster id
            "name": None,  # (str) cluster name
            "namespace": None,  # (str) deleted pod's namespace
            "pod": None,  # (str) deleted pod name
            "result": {
                "success": False,  # (bool) is success?
                "stdout": None,  # (str) stdout message
                "error": None  # (str)
            }
        }

    @staticmethod
    def get_pod_migratable_cluster_view_model() -> dict:
        """
        get pod migratable cluster view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) cluster name
            "id": None,  # (str) cluster uuid
            "nodes": []  # (str) node list
        }

    @staticmethod
    def get_pod_migratable_cluster_list_view_model() -> dict:
        """
        get pod migratable cluster list view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) cluster name
            "id": None,  # (str) cluster uuid
            "clusters": []
        }

    @staticmethod
    def get_do_pod_migrate_view_model() -> dict:
        """
        get do pod migrate view model
        :return: (dict)
        """
        return {
            "name": None,  # request cluster name
            "id": None,  # request cluster id
            "namespace": None,  # migrate source namespace
            "pod": None,  # migrate source pod
            "target": {  # migration target
                "cluster": None,  # (str) migration target cluster name
                "id": None,  # (str) migration target cluster id
                "node": None,  # (str) migration target cluster node
            },
            "stime": None,  # (str) migration start time
            "age": None
        }

    @staticmethod
    def get_cluster_migration_log_view() -> dict:
        """
        get cluster migration log view
        :return:
        """
        return {
            "migration_id": None,       # migration ID
            "source_cluster": None,     # source cluster name
            "source_pod": None,         # source pod name
            "target_cluster": None,     # target cluster name
            "target_node": None,        # target node name
            "task": None,               # current task
            "state": None,             # migration state('ISSUED', 'RUNNING', 'DONE', 'PENDING', 'ERROR_EXITED', 'COMPLETED', 'UNKNOWN')
            "retry": None,              # retry count in current task
            "error": None,              # error message
            "start_date": None,         # start datetime
            "end_date": None            # end datetime
        }

    @staticmethod
    def get_cluster_migration_log_list_view() -> dict:
        """
        get cluster migration log list view
        :return:
        """
        return {
            "name": None,   # (str) cluster name
            "id": None,     # (str) cluster id
            "logs": [],     # (list[migration_log_view_model from get_cluster_migration_log_view()]
        }

    @staticmethod
    def get_delete_pod_migration_log_view() -> dict:
        """
        get cluster migration log list view
        :return:
        """
        return {
            "name": None,   # (str) cluster name
            "id": None,     # (str) cluster uuid
            "result": {
                "success": False,   # (bool) is success?
                "error": False      # (bool) error message
            }
        }

    @staticmethod
    def get_daemonset_view_model() -> dict:
        """
        get daemonSet view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) daemonset name
            "state": None,  # (str) daemonset state("Active" or "NotReady" or "Terminating")
            "namespace": None,  # (str) namespace name
            "images": [],  # (list[str]) docker image list
            "desired": None,  # (int) desired
            "current": None,  # (int) current
            "ready": None,  # (int) ready
            "conditions": [],  # list[condition_view_model from get_condition_view_model()]
            "stime": None,  # (str) daemonset state time
            "age": None
        }

    @staticmethod
    def get_daemonset_list_view_model() -> dict:
        """
        get daemonset list view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) cluster name
            "id": None,  # (str) cluster id
            "daemonsets": []  # list[daemonset_view_model from get_daemonset_view_model()]
        }

    @staticmethod
    def get_daemonset_deletion_view_model() -> dict:
        """
        get daemonset deletion view model
        :return: (dict)
        """
        return {
            "id": None,  # (str) request cluster id
            "name": None,  # (str) request cluster name
            "namespace": None,  # (str) deleted daemonset namespace
            "daemonset": None,  # (str) deleted daemonset
            "result": {
                "success": False,  # (bool) is success?
                "stdout": None,  # (str) stdout message
                "error": None  # (str)
            }
        }

    @staticmethod
    def get_deployment_view_model() -> dict:
        """
        get deployment view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) deployments name
            "state": None,  # (str) deployment state("Active" or "NotReady" or "Terminating")
            "namespace": None,  # (str) namespace name
            "images": [],  # (list[str]) docker image list
            "ready_replicas": None,  # (int) number of ready replica
            "replicas": None,  # (int) number of total replica
            "restart": None,  # (int) number of restart replica
            "selector": [],  # (list(str)) pod selector list
            "conditions": [],  # list[condition_view_model from get_condition_view_model()]
            "stime": None,  # (str) deployment start time
            "age": None
        }

    @staticmethod
    def get_deployment_list_view_model() -> dict:
        """
        get deployment list view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) cluster name
            "id": None,  # (str) cluster id
            "deployments": []  # list[deployment_view_model from get_deployment_view_model()]
        }

    @staticmethod
    def get_deployment_deletion_view_model() -> dict:
        """
        get deployment deletion view model
        :return: (dict)
        """
        return {
            "id": None,  # request cluster id
            "name": None,  # request cluster name
            "namespace": None,  # deleted deployment's namespace
            "deployment": None,  # deleted deployment
            "result": {
                "success": False,  # (bool) is success?
                "stdout": None,  # (str) stdout message
                "error": None  # (str)
            }
        }
