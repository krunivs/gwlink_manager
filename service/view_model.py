class ServiceViewModel:
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
    def get_service_export_view_model() -> dict:
        """
        get service export view model
        :return: (dict)
        """
        return {
            "status": None,  # (str) "true" or "false"
            "target": None,  # (str) export cluster name
            "reason": None,  # (str) service export error reason
            "clusterset_ip": None,  # (str) exported service ip
            "service_discovery": None,  # (str) export target service dns("vlc-http.etri.svc.clusterset.local")
            "stime": None,  # (str) export datetime("2021-05-26 23:53:56")
            "age": None,  # (str)
        }

    @staticmethod
    def get_port_view_model() -> dict:
        """
        get port view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) port name("http")
            "port": None,  # (str) service port name("8080")
            "node_port": None,  # (str) node port("31001")
            "target_port": None,  # (str) container port("80")
            "protocol": None,  # (str) TCP or UDP("TCP")
        }

    @staticmethod
    def get_service_view_model() -> dict:
        """
        get service view model
        :return: (dict)
        """
        return {
            "name": 'None',  # (str) service name
            "state": 'None',  # (str) service state("Active" or "NotReady" or "Terminating")
            "service_export": 'None',  # (service_export_view_model)
            "namespace": 'None',  # (str) namespace name
            "service_type": 'None',  # (str) service type("ClusterIP" or "NodePort" or "LoadBalancer" or "ExternalName")
            "cluster_ip": 'None',  # (str) service cluster ip
            "external_ips": [],  # (list[str]) service external ip
            "ports": [],  # list[port_view_model from get_port_view_model()]
            "selector": [],  # list[str](["app:proxy-vlc-http"])
            "conditions": [],  # list[condition_view_model]
            "stime": None,  # (str) service start datetime("2021-10-26 23:53:56")
            "age": None,  # (str)
        }

    @staticmethod
    def get_service_list_view_model() -> dict:
        """
        get service list view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) cluster name
            "id": None,  # (str) cluster id
            "services": []  # (list[service_view_model from get_service_view_model()])
        }

    @staticmethod
    def get_service_deletion_view_model() -> dict:
        """
        get service deletion view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) cluster name
            "id": None,  # (str) cluster uuid
            "namespace": None,  # (str) namespace
            "service": None,  # (str) delete service
            "result": {
                "success": False,  # (bool) is success?
                "stdout": False,  # (str) stdout message
                "error": False,  # (str) error message
            }
        }

    @staticmethod
    def get_do_service_export_view_model() -> dict:
        """
        get service export view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) cluster name
            "id": None,  # (str) cluster uuid
            "namespace": None,  # (str) export service namespace
            "service": None,  # (str) export service name
            "result": {
                "success": False,  # (bool) is success?
                "stdout": False,  # (str) stdout message
                "error": False,  # (str) error message
            }
        }

    @staticmethod
    def get_do_service_unexport_view_model() -> dict:
        """
        get service unexport view model
        :return: (dict)
        """
        return {
            "name": None,  # (str) cluster name
            "id": None,  # (str) cluster uuid
            "namespace": None,  # (str) unexport service namespace
            "service": None,  # (str) unexport service name
            "result": {
                "success": False,  # (bool) is success?
                "stdout": False,  # (str) stdout message
                "error": False,  # (str) error message
            }
        }
