class ClusterViewModel:
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
    def get_cluster_component_condition_view_model() -> dict:
        """
        get cluster component list view model
        :return: (dict)
        """
        return {
            "id": None,  # (str) cluster uuid
            "name": None,  # (str) cluster name
            "conditions": []  # list[condition_view_model from get_condition_view_model()]
        }

    @staticmethod
    def get_cluster_list_view_model() -> dict:
        """
        get cluster list view model
        :return: (dict)
        """
        return {
            "clusters": []
        }

    @staticmethod
    def get_cluster_view_model() -> dict:
        """
        get cluster view model
        :return: (dict)
        """
        return {
            "id": None,  # (str) cluster uuid
            "name": None,  # (str) cluster name
            "desc": None,  # (str) cluster description
            "state": None,  # (str) cluster state("Active" or "Pending" or "Unavailable")
            "api_address": None,  # (str) cluster's kube-api-server url
            "api_version": None,  # (str) cluster's kube-api-server version
            "registration": None,  # (str) cluster registration command(should execute in cluster's master node shell)
            "nodes": 0,  # (int) number of nodes in cluster
            "mc_network": {
                "connect_id": None,  # multi-cluster network id
                "status": None,  # (str) MC network status("connected" or "unavailable")
                "status_label": "label-unavailable", # status label design("label-connected" or "label-unavailable")
                "globalnet": None,  # (str) global vpn is enabled?("enabled" or "disabled")
                "global_cidr": None,  # (str) global vpn subnet range("244.0.0.0/8")
                "cable_driver": None,  # (str) tunneling driver("wireguard" or "libswan" or "ipsec")
                "broker_role": None,
                "local": {
                    "name": None,  # (str) cluster name
                    "public": None,  # (str) public ip("211.237.16.76")
                    "gateway": None,  # (str) gateway ip("10.0.0.206")
                    "service_cidr": None,  # (str) service network("10.55.0.0/16")
                    "cluster_cidr": None  # (str) pod network("10.244.0.0/16")
                },
                "remote": {
                    "name": None,  # (str) cluster name
                    "public": None,  # (str) public ip("211.237.16.76")
                    "gateway": None,  # (str) gateway ip("10.0.0.208")
                    "service_cidr": None,  # (str) service network("10.55.0.0/16")
                    "cluster_cidr": None  # (str) pod network("10.244.0.0/16")
                }
            },
            "conditions": []  # list[condition_view_model from get_condition_view_model()]
        }

    @staticmethod
    def get_cluster_name_list_view_model() -> dict:
        """
        get cluster name list view model
        :return: (dict)
        """
        return {
            "clusters": []  # list[cluster_name_view_model from get_cluster_name_view_model()]
        }

    @staticmethod
    def get_cluster_name_view_model():
        """
        get cluster name view model
        :return: (dict)
        """
        return {
            "id": None,     # cluster uuid
            "name": None,   # cluster name
        }

    @staticmethod
    def get_cluster_deletion_view_model():
        """
        get cluster deletion view model
        :return: (dict)
        """
        return {
            "id": None,  # cluster uuid
            "name": None,  # cluster name
            "result": {
                "success": None,  # is success?
                "stdout": None,  # stdout message
                "error": None,  # error message
            }
        }

    @staticmethod
    def get_node_list_view_model():
        """
        get node list view model
        :return: (dict)
        """
        return {
            "name": None,  # cluster name
            "id": None,  # cluster uuid
            "nodes": [],  # list[node_view_model from get_node_view_model()]
        }

    @staticmethod
    def get_node_view_model():
        """
        get node view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) node's hostname
            "host_if": None,  # (str) node's network interface for extern ip(i.e., eth0)
            "ip": None,  # (str) node's extern ip address
            "state": None,  # (str) node state("Pending" or "Running" or "Terminated")
            "role": None,  # (str) "Worker" or "Master"
            "k8s_version": None,  # (str) kubernetes version
            "os": None,  # (str) node's OS
            "number_of_cpu": None,  # (int) maximum number of CPU cores
            "ram_size": None,  # (str) total installed memory size
            "pods": {
                "max_pods": None,  # (str) number of maximum deployable pods
                "running_pods": None,  # (str) number of running pods
                "usage": None,  # (str) pod usage(running pods/max pods*100;%)
            },
            "stime": None,  # (str) node start time(yyyy-MM-dd HH:mm:SS.f)
            "age": None
        }

    @staticmethod
    def get_node_metric_view_model():
        """
        get node metric view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) node hostname
            "pods": {
                "max_pods": None,  # (str) number of maximum deployable pods
                "running_pods": None,   # (str) number of running pods
                "usage": None,  # (str) pod usage(running pods/max pods*100;%)
            },
            "cpu_total": None,  # (str) number of total cpus installed
            "cpu_usages": [],   # list[[(float)timestamp, (float)usage ratio(%)], ]
            "mem_total": None,  # (str) size of total memory installed
            "mem_usages": [],   # list[[(float)timestamp, (float)usage ratio(%)], ]
            "net_tx_bytes": [],     # list[[(float)timestamp, (int)tx byte], ]
            "net_rx_bytes": [],     # list[[(float)timestamp, (int)rx byte], ]
        }

    @staticmethod
    def get_node_metric_list_view_model():
        """
        get node metric list view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) cluster name
            "id": None,  # (str) cluster uuid
            "nodes": []  # (list[node_metric_view_model from get_node_metric_view_model()])
        }

    @staticmethod
    def get_mc_network_metric_view_model():
        """
        get multi-cluster throughput view model
        :return: (dict)
        """
        return {
            "tx_bytes": None,   # (list[[(float)timestamp, (int)tx byte], ])
            "rx_bytes": None,   # (list[[(float)timestamp, (int)rx byte], ])
            "latencies": None,  # (list[[(float)timestamp, (float)latencies], ])
        }

    @staticmethod
    def get_mc_network_control_view_model():
        """
        get multi-cluster network control view
        :return: (dict)
        """
        return {
            "name": None,  # (str) cluster name
            "id": None,  # (str) cluster uuid
            "error": None  # (str) error message
        }

    @staticmethod
    def get_resource_manifest_control_view_model():
        """
        get apply resource manifest view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) cluster name
            "id": None,  # (str) cluster uuid
            "result": {
                "success": None,  # (str) is success?
                "stdout": None,  # (str) stdout message
                "error": None,  # (str) error message
            }
        }

    @staticmethod
    def get_diagnose_multi_cluster_network_failure_view_model():
        """
        get diagnosis of multi-cluster network failure view model
        :return: (dict)
        """
        return {
            "cluster_name": None, # (str) request cluster name
            "result": None # (str) diagnosis result(in repository.common.typeMultiClusterNetworkDiagnosis(Enum))
        }

    @staticmethod
    def get_join_broker_info_view_model():
        """
        get join broker info view model
        :return: (dict)
        """
        return {
            "mc_connect_id": None,  # (str) multi-cluster connection id(uuid4 format)
            "result": None, # (str) broker-info.subm content
        }