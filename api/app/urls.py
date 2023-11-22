from django.urls import path

from . import views

"""
 App API urls which is called to app(i.e., Web, 3rd-party) 
"""
api_version = 'v1'

urlpatterns = [
    # Cluster management APIs
    ## (IFD0001_CLS_001) retrieve cluster list
    ### GET /api/app/v1/clusters
    ## (IFD0001_CLS_001.01) retrieve cluster list filtered by cluster name
    ### GET /api/app/v1/clusters?filter=name
    ## (IFD001_CLS_003) register cluster
    ### POST /api/app/v1/clusters
    path(api_version +
         '/clusters',
         views.manage_clusters, name='clusters'),

    ## (IFD001_CLS_002) retrieve specified cluster
    ### GET /api/app/v1/clusters/<str:cluster>
    ## (IFD001_CLS_004) delete specified cluster
    ### DELETE /api/app/v1/clusters/<str:cluster>
    path(api_version +
         '/clusters/<str:cluster>',
         views.manage_cluster, name='cluster'),

    ## (IFD001_CLS_002.1) get conditions for cluster's primary components
    ### GET /api/app/v1/clusters/<str:cluster>/conditions
    path(api_version +
         '/clusters/<str:cluster>/conditions',
         views.get_cluster_components_conditions, name='cluster'),

    ## (IFD001_CLS_005) connect multicluster network
    ### POST /api/app/v1/clusters/<str:cluster>/mc/connect
    path(api_version +
         '/clusters/<str:cluster>/mc/connect',
         views.connect_mc_network, name='connect_mc_network'),

    ## (IFD001_CLS_006) disconnect multicluster network
    ### POST /api/app/v1/clusters/<str:cluster>/mc/disconnect
    path(api_version +
         '/clusters/<str:cluster>/mc/disconnect',
         views.disconnect_mc_network, name='disconnect_mc_network'),

    # deprecated! 23-11-13
    ## (IFD001_CLS_007) retrieve multicluster network latency
    ### GET /api/app/v1/clusters/<str:cluster>/mc/metrics/latency
    # path(api_version +
    #      '/clusters/<str:cluster>/mc/metrics/latency',
    #      views.get_mc_latency, name='mc_latency'),

    ##  IFD001_CLS_008) retrieve multicluster network usage
    ### GET /api/app/v1/clusters/<str:cluster>/mc/<str:endpoint>/metrics
    path(api_version +
         '/clusters/<str:cluster>/mc/<str:endpoint>/metrics',
         views.get_mc_network_metrics, name='mc_metrics'),

    # Node management APIs
    ## (IFD001_NODE_001) retrieve node list
    ### GET /api/app/v1/clusters/<str:cluster>/nodes
    path(api_version +
         '/clusters/<str:cluster>/nodes',
         views.get_nodes, name='nodes'),

    ## (IFD001_NODE_002) retrieve specified node
    ### GET /api/app/v1/clusters/<str:cluster>/nodes/<str:node>
    path(api_version +
         '/clusters/<str:cluster>/nodes/<str:node>',
         views.get_node, name='node'),

    ## (IFD001_NODE_003) retrieve specified node metrics
    ### GET /api/app/v1/clusters/<str:cluster>/nodes/<str:node>/metrics
    path(api_version +
         '/clusters/<str:cluster>/nodes/<str:node>/metrics',
         views.get_node_metrics, name='node_usages'),

    # Kubernetes resource management APIs
    # Namespace management APIs
    ## (IFD001_NS_001) retrieve kubernetes namespace list
    ### GET /api/app/v1/clusters/<str:cluster>/namespaces
    path(api_version +
         '/clusters/<str:cluster>/namespaces',
         views.get_namespace_list, name='namespace_list'),

    ## (IFD001_NS_002) delete kubernetes namespace
    ### DELETE /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>
    path(api_version +
         '/clusters/<str:cluster>/namespaces/<str:namespace>',
         views.manage_namespace, name='namespace'),



    # Pod management APIs
    ## (IFD001_POD_001) retrieve kubernetes pod list
    ### GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/pods
    ## (IFD001_POD_002) retrieve kubernetes pod list filtered by service or deployment, daemonset
    ### GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/pods?service=<str:service>
    ### GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/pods?deployment=<str:deployment>
    ### GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/pods?daemonset=<str:daemonset>
    path(api_version +
         '/clusters/<str:cluster>/namespaces/<str:namespace>/pods',
         views.get_pod_list, name='pods'),

    ## (IFD001_POD_003) retrieve kubernetes specified pod
    ### GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/pods/<str:pod>
    ## (IFD001_POD_004) delete kubernetes specified pod
    ### DELETE /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/pods/<str:pod>
    path(api_version +
         '/clusters/<str:cluster>/namespaces/<str:namespace>/pods/<str:pod>',
         views.manage_pod, name='pod'),

    ## (IFD001_POD_005) retrieve kubernetes pod migration hint
    ### GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/pods/<str:pod>/migrate
    ## (IFD001_POD_006) run kubernetes pod migration
    ### POST /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/pods/<str:pod>/migrate
    path(api_version +
         '/clusters/<str:cluster>/namespaces/<str:namespace>/pods/<str:pod>/migrate',
         views.manage_pod_migration, name='pod_migration'),

    ## (IFD001_POD_007) retrieve pod migration log list
    ### POST /api/app/v1/clusters/<str:cluster>/migration_logs
    path(api_version +
         '/clusters/<str:cluster>/migration_logs',
         views.manage_pod_migration_log_list, name='cluster_pod_migration_logs'),

    ## (IFD001_POD_008) delete pod migration log
    ### POST /api/app/v1/clusters/<str:cluster>/migration_logs/<str:migration_id>
    path(api_version +
         '/clusters/<str:cluster>/migration_logs/<str:migration_id>',
         views.manage_pod_migration_log, name='delete_pod_migration_log'),

    # Service management APIs
    ## (IFD001_SERVICE_001) retrieve kubernetes service list
    ### GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/services
    ## (IFD001_SERVICE_002) retrieve kubernetes service list filtered by pod
    ### GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/services?pod=<str:pod>
    path(api_version +
         '/clusters/<str:cluster>/namespaces/<str:namespace>/services',
         views.get_service_list, name='service_list'),

    ## (IFD001_SERVICE_003) retrieve kubernetes specified service
    ### GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/services/<str:service>
    ## (IFD001_SERVICE_004) delete kubernetes specified service
    ### DELETE /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/services/<str:service>
    path(api_version +
         '/clusters/<str:cluster>/namespaces/<str:namespace>/services/<str:service>',
         views.manage_service, name='service'),

    ## (IFD001_SERVICE_005) export service to connected cluster
    ### POST /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/services/<str:service>/export
    path(api_version +
         '/clusters/<str:cluster>/namespaces/<str:namespace>/services/<str:service>/export',
         views.export_service, name='export_service'),

    ## (IFD001_SERVICE_006) unexport service from connected cluster
    ### POST /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/services/<str:service>/unexport
    path(api_version +
         '/clusters/<str:cluster>/namespaces/<str:namespace>/services/<str:service>/unexport',
         views.unexport_service, name='unexport_service'),

    # Deployment management APIs
    ## (IFD001_DEPLOY_001) retrieve kubernetes deployment list
    ### GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/deployments
    ## (IFD001_DEPLOY_002) retrieve kubernetes deployment list filtered by pod
    ### GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/deployments?pod=<str:pod>
    path(api_version +
         '/clusters/<str:cluster>/namespaces/<str:namespace>/deployments',
         views.get_deployment_list, name='deployment_list'),

    ## (IFD001_DEPLOY_003) retrieve kubernetes specified deployment
    ### GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/deployments/<str:deployment>
    ## (IFD001_DEPLOY_004) delete kubernetes specified deployment
    ### DELETE /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/deployments/<str:deployment>
    path(api_version +
         '/clusters/<str:cluster>/namespaces/<str:namespace>/deployments/<str:deployment>',
         views.manage_deployment, name='deployment'),

    # DaemonSet management APIs
    ## (IFD001_DAEMON_001) retrieve kubernetes daemonset list
    ### GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/daemonsets
    ## (IFD001_DAEMON_002) retrieve kubernetes daemonset list filtered by pod
    ### GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/daemonsets?pod=<str:pod>
    path(api_version +
         '/clusters/<str:cluster>/namespaces/<str:namespace>/daemonsets',
         views.get_daemonset_list, name='daemonset_list'),

    ## (IFD001_DAEMON_003) retrieve kubernetes specified daemonset
    ### GET /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/daemonsets/<str:daemonset>
    ## (IFD001_DAEMON_004) delete kubernetes specified daemonset
    ### DELETE /api/app/v1/clusters/<str:cluster>/namespaces/<str:namespace>/daemonsets/<str:daemonset>
    path(api_version +
         '/clusters/<str:cluster>/namespaces/<str:namespace>/daemonsets/<str:daemonset>',
         views.manage_daemonset, name='daemonset'),

    # Kubernetes manifest APIs
    ## (IFD001_MANIFEST_001) apply kubernetes manifest
    ### POST /api/app/v1/clusters/<str:cluster>/manifest/apply
    path(api_version +
         '/clusters/<str:cluster>/manifest/apply',
         views.apply_manifest, name='manifest'),

    ## (IFD001_MANIFEST_002) delete kubernetes manifest
    ### POST /api/app/v1/clusters/<str:cluster>/manifest/delete
    path(api_version +
         '/clusters/<str:cluster>/manifest/delete',
         views.delete_manifest, name='manifest'),

    ## (IFD001_MANIFEST_003) validate kubernetes manifest
    ### POST /api/app/v1/clusters/<str:cluster>/manifest/validate
    path(api_version +
         '/clusters/<str:cluster>/manifest/validate',
         views.validate_manifest, name='manifest'),

    # GW-AGENT install
    path(api_version +
         '/clusters/<str:cluster>/gw-agent',
         views.get_gw_agent, name='get gw-agent'),
]