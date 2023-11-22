from cluster.common.type import Event
from repository.cache.cluster import ClusterCache
from repository.common.type import Kubernetes, NetStat, Metric
from api.agent.event_view import EventObject

class EventDispatcher:
    """
    Agent event dispatcher
    """
    @staticmethod
    def dispatch(cluster_id, body):
        """
        dispatch event
        :param cluster_id: (str) cluster id
        :param body: (dict) see EventObject
        :return:
        """
        if 'event_type' not in body:
            stderr = 'Not found event_type key in body'
            raise KeyError(stderr)

        if 'object_type' not in body:
            stderr = 'Not found object_type key in body'
            raise KeyError(stderr)

        if 'object_value' not in body:
            stderr = 'Not found object_value key in body'
            raise KeyError(stderr)

        cluster_cache = ClusterCache().get_cluster(cluster_id)

        # case of cluster session is not registered in center cache
        if cluster_cache is None:
            return

        # dispatch event
        event = EventObject.to_object(body)

        # get cluster cache
        cluster_cache = ClusterCache().get_cluster(cluster_id)

        if cluster_cache is None:
            raise ValueError('No cluster cache entry for cluster_id {}'.format(cluster_id))

        # Dispatch event
        if event.object_type == Kubernetes.COMPONENTS.value:
            EventDispatcher.dispatch_components(cluster_cache, event)
            return

        elif event.object_type == Kubernetes.NODE.value:
            EventDispatcher.dispatch_node(cluster_cache, event)
            return

        elif event.object_type == Kubernetes.NAMESPACE.value:
            EventDispatcher.dispatch_namespace(cluster_cache, event)
            return

        elif event.object_type == Kubernetes.POD.value:
            EventDispatcher.dispatch_pod(cluster_cache, event)
            return

        elif event.object_type == Kubernetes.DEPLOYMENT.value:
            EventDispatcher.dispatch_deployment(cluster_cache, event)
            return

        elif event.object_type == Kubernetes.DAEMONSET.value:
            EventDispatcher.dispatch_daemonset(cluster_cache, event)
            return
        elif event.object_type == Kubernetes.SERVICE.value:
            EventDispatcher.dispatch_service(cluster_cache, event)
            return

        elif event.object_type == NetStat.MULTI_CLUSTER_NETWORK.value:
            EventDispatcher.dispatch_mcn(cluster_cache, event)
            return

        elif event.object_type == NetStat.ENDPOINT_NETWORK.value:
            EventDispatcher.dispatch_mcn_endpoint(cluster_cache, event)
            return

        elif event.object_type == NetStat.SERVICE_IMPORT.value:
            EventDispatcher.dispatch_mcn_service_import(cluster_cache, event)
            return

        elif event.object_type == NetStat.SERVICE_IMPORTS.value:
            EventDispatcher.dispatch_mcn_service_imports(cluster_cache, event)
            return

        elif event.object_type == NetStat.SERVICE_EXPORT.value:
            EventDispatcher.dispatch_mcn_service_export(cluster_cache, event)
            return

        elif event.object_type == NetStat.SERVICE_EXPORTS.value:
            EventDispatcher.dispatch_mcn_service_exports(cluster_cache, event)
            return

        elif event.object_type == Metric.MULTI_CLUSTER_METRIC.value:
            EventDispatcher.dispatch_mcn_metric(cluster_cache, event)
            return

        elif event.object_type == Metric.NODE_METRIC.value:
            EventDispatcher.dispatch_node_metric(cluster_cache, event)
            return

        else:
            raise ValueError('Invalid event_type({}) in body'.format(event.event_type))

    @staticmethod
    def dispatch_components(cluster_cache, event: EventObject):
        """
        dispatch components event
        :param cluster_cache: (dict)
        :param event: (EventObject)
        :return:
        """
        if event.event_type == Event.ADDED.value or event.event_type == Event.MODIFIED.value:
            cluster_cache['component'].set_conditions(event.object_value)
            return

    @staticmethod
    def dispatch_node(cluster_cache, event: EventObject):
        """
        dispatch node event
        :param cluster_cache: (dict) cluster cache from repository.cache.cluster.ClusterCache._cluster[cluster_id]
        :param event: (EventObject) event object
        :return:
        """
        if event.event_type == Event.DELETED.value:
            cluster_cache['resource'].delete(event.object_value)
            return

        if event.event_type == Event.ADDED.value or event.event_type == Event.MODIFIED.value:
            cluster_cache['resource'].create_or_update(event.object_value)
            return

    @staticmethod
    def dispatch_namespace(cluster_cache, event: EventObject):
        """
        dispatch namespace event
        :param cluster_cache: (dict) cluster cache from repository.cache.cluster.ClusterCache._cluster[cluster_id]
        :param event: (EventObject) event object
        :return:
        """
        if event.event_type == Event.DELETED.value:
            cluster_cache['resource'].delete(event.object_value)
            return

        if event.event_type == Event.ADDED.value or event.event_type == Event.MODIFIED.value:
            cluster_cache['resource'].create_or_update(event.object_value)
            return

    @staticmethod
    def dispatch_pod(cluster_cache, event: EventObject):
        """
        dispatch pod event
        :param cluster_cache: (dict) cluster cache from repository.cache.cluster.ClusterCache._cluster[cluster_id]
        :param event: (EventObject) event object
        :return:
        """
        if event.event_type == Event.DELETED.value:
            cluster_cache['resource'].delete(event.object_value)
            return

        if event.event_type == Event.ADDED.value or event.event_type == Event.MODIFIED.value:
            cluster_cache['resource'].create_or_update(event.object_value)
            return

    @staticmethod
    def dispatch_deployment(cluster_cache, event: EventObject):
        """
        dispatch deployment event
        :param cluster_cache: (dict) cluster cache from repository.cache.cluster.ClusterCache._cluster[cluster_id]
        :param event: (EventObject) event object
        :return:
        """
        if event.event_type == Event.DELETED.value:
            cluster_cache['resource'].delete(event.object_value)
            return

        if event.event_type == Event.ADDED.value or event.event_type == Event.MODIFIED.value:
            cluster_cache['resource'].create_or_update(event.object_value)
            return

    @staticmethod
    def dispatch_daemonset(cluster_cache, event: EventObject):
        """
        dispatch daemonset event
        :param cluster_cache: (dict) cluster cache from repository.cache.cluster.ClusterCache._cluster[cluster_id]
        :param event: (EventObject) event object
        :return:
        """
        if event.event_type == Event.DELETED.value:
            cluster_cache['resource'].delete(event.object_value)
            return

        if event.event_type == Event.ADDED.value or event.event_type == Event.MODIFIED.value:
            cluster_cache['resource'].create_or_update(event.object_value)
            return

    @staticmethod
    def dispatch_service(cluster_cache, event: EventObject):
        """
        dispatch service event
        :param cluster_cache: (dict) cluster cache from repository.cache.cluster.ClusterCache._cluster[cluster_id]
        :param event: (EventObject) event object
        :return:
        """
        if event.event_type == Event.DELETED.value:
            cluster_cache['resource'].delete(event.object_value)
            return

        if event.event_type == Event.ADDED.value or event.event_type == Event.MODIFIED.value:
            cluster_cache['resource'].create_or_update(event.object_value)
            return

    @staticmethod
    def dispatch_mcn(cluster_cache, event: EventObject):
        """
        dispatch multicluster network
        :param cluster_cache: (dict) cluster cache from repository.cache.cluster.ClusterCache._cluster[cluster_id]
        :param event: (EventObject) event object
        :return:
        """
        if event.event_type == Event.DELETED.value:
            cluster_cache['network'].clear()
            return

        if event.event_type == Event.ADDED.value or event.event_type == Event.MODIFIED.value:
            cluster_cache['network'].set_mc_network(event.object_value)
            return

    @staticmethod
    def dispatch_mcn_endpoint(cluster_cache, event: EventObject):
        """
        dispatch multicluster network endpoint
        :param cluster_cache: (dict) cluster cache from repository.cache.cluster.ClusterCache._cluster[cluster_id]
        :param event: (EventObject) event object
        :return:
        """
        mc_network = cluster_cache['network'].get_mc_network()

        if mc_network is None:
            raise SystemError('Not found mc_network')

        if event.event_type == Event.DELETED.value:
            mc_network.delete_endpoint(event.object_value)
            return

        if event.event_type == Event.ADDED.value or event.event_type == Event.MODIFIED.value:
            mc_network.set_endpoint(event.object_value)
            return

    @staticmethod
    def dispatch_mcn_service_import(cluster_cache, event: EventObject):
        """
        dispatch multicluster service import
        :param cluster_cache: (dict) cluster cache from repository.cache.cluster.ClusterCache._cluster[cluster_id]
        :param event: (EventObject) event object
        :return:
        """
        mc_network_service = cluster_cache['network'].get_mc_network_service()

        if mc_network_service is None:
            error = 'Not found mc_network_service'
            raise SystemError(error)

        if event.event_type == Event.DELETED.value:
            mc_network_service.delete_service_import(event.object_value)
            return

        if event.event_type == Event.ADDED.value or event.event_type == Event.MODIFIED.value:
            mc_network_service.set_service_import(event.object_value)
            return

    @staticmethod
    def dispatch_mcn_service_imports(cluster_cache, event: EventObject):
        """
        dispatch multicluster service imports
        :param cluster_cache: (dict) cluster cache from repository.cache.cluster.ClusterCache._cluster[cluster_id]
        :param event: (EventObject) event object
        :return:
        """
        mc_network_service = cluster_cache['network'].get_mc_network_service()

        if mc_network_service is None:
            error = 'Not found mc_network_service'
            raise SystemError(error)

        if event.event_type == Event.ADDED.value or event.event_type == Event.MODIFIED.value:
            mc_network_service.set_service_imports(event.object_value)
            return

    @staticmethod
    def dispatch_mcn_service_export(cluster_cache, event: EventObject):
        """
        dispatch multicluster service export
        :param cluster_cache: (dict) cluster cache from repository.cache.cluster.ClusterCache._cluster[cluster_id]
        :param event: (EventObject) event object
        :return:
        """
        mc_network_service = cluster_cache['network'].get_mc_network_service()

        if mc_network_service is None:
            error = 'Not found mc_network_service'
            raise SystemError(error)

        if event.event_type == Event.DELETED.value:
            mc_network_service.delete_service_export(event.object_value)
            return

        if event.event_type == Event.ADDED.value or event.event_type == Event.MODIFIED.value:
            mc_network_service.set_service_export(event.object_value)
            return

    @staticmethod
    def dispatch_mcn_service_exports(cluster_cache, event: EventObject):
        """
        dispatch multicluster service exports
        :param cluster_cache: (dict) cluster cache from repository.cache.cluster.ClusterCache._cluster[cluster_id]
        :param event: (EventObject) event object
        :return:
        """
        mc_network_service = cluster_cache['network'].get_mc_network_service()

        if mc_network_service is None:
            error = 'Not found mc_network_service'
            raise SystemError(error)

        if event.event_type == Event.ADDED.value or event.event_type == Event.MODIFIED.value:
            mc_network_service.set_service_exports(event.object_value)
            return

    @staticmethod
    def dispatch_mcn_metric(cluster_cache, event: EventObject):
        """
        dispatch multicluster metric
        :param cluster_cache: (dict) cluster cache from repository.cache.cluster.ClusterCache._cluster[cluster_id]
        :param event: (EventObject) event object
        :return:
        """
        if event.event_type == Event.DELETED.value:
            cluster_cache['metric'].delete_mc_network()
            return

        if event.event_type == Event.ADDED.value or event.event_type == Event.MODIFIED.value:
            cluster_cache['metric'].set_mc_network(event.object_value)
            return

    @staticmethod
    def dispatch_node_metric(cluster_cache, event: EventObject):
        """
        dispatch node metric
        :param cluster_cache: (dict) cluster cache from repository.cache.cluster.ClusterCache._cluster[cluster_id]
        :param event: (EventObject) event object
        :return:
        """
        if event.event_type == Event.DELETED.value:
            cluster_cache['metric'].delete_node(event.object_value)
            return

        if event.event_type == Event.ADDED.value or event.event_type == Event.MODIFIED.value:
            if event.object_value.mem_metric:
                for usage in event.object_value.mem_metric.usages:
                    usage[1] *= 100

            cluster_cache['metric'].set_node_object(event.object_value)
            return

