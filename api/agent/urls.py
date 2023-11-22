from django.urls import path
from .views import *

"""
 Agent API url which is supported to 'CEdge-agent' 
"""
api_version = 'v1'

urlpatterns = [
    # get keep_alive
    # POST /api/agent/v1/cluster/<str:cluster>/keep_alive
    path(api_version +
         '/cluster/<str:cluster>/keep_alive', keep_alive),

    # push event
    # PUT /api/agent/v1/cluster/<str:cluster>/event
    path(api_version +
         '/cluster/<str:cluster>/event', push_event),

    # register cluster session
    # POST /api/agent/v1/cluster/:cluster/initialize
    path(api_version +
         '/cluster/<str:cluster>/initialize', initialize_cluster),

    # push response
    # PUT /api/agent/v1/cluster/<str:cluster>/request/<str:request_id>
    path(api_version +
         '/cluster/<str:cluster>/request/<str:request_id>', push_response),

    # get multi-cluster network diagnosis
    # GET /api/agent/v1/cluster/<str:cluster>/mcn/diagnosis
    path(api_version +
         '/cluster/<str:cluster>/mcn/diagnosis', diagnose_multi_cluster_network),

    # get join broker
    # GET /api/agent/v1/mcn/<str:mc_connect_id>/broker
    path(api_version +
         '/mcn/<str:mc_connect_id>/broker', get_join_broker_info),

]