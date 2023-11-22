from django.shortcuts import render, redirect
from rest_framework.authtoken.models import Token
from account.models import User

# controllers
from cluster import views as cluster_views
from workloads import views as workload_views
from service import views as service_views
import logging

logger = logging.getLogger(__name__)

number_of_default_view_contents = 5

"""
Desc: present center UI 
"""
def authorize_user(request):
    """
    authorize user session with token
    :param request:
    :return:
    """
    token_key = request.COOKIES.get("token")

    if Token.objects.filter(key=token_key).exists():
        token = Token.objects.get(key=token_key)

    else:
        error = 'Unauthorized: fail to authorize user account'
        logger.warning(error)
        raise PermissionError(error)

    if User.objects.filter(email=token.user).exists():
        return User.objects.get(email=token.user)

    else:
        error = 'Unauthorized: fail to authorize user account'
        logger.warning(error)
        raise PermissionError(error)


def get_resource_target(request):
    """
    get target resource(selected_cluster, selected_namespace) from COOKIES
    :param request:
    :return:
    """
    selected_cluster = request.COOKIES.get("selected_cluster", None)
    selected_namespace = request.COOKIES.get("selected_namespace", None)

    if not selected_cluster:
        error_message = 'Not exist \'selected_cluster\' in COOKIES'
        logger.error(error_message)
        raise ValueError(error_message)

    if not selected_namespace:
        error_message = 'Not exist \'selected_namespace\' in COOKIES'
        logger.error(error_message)
        raise ValueError(error_message)

    return selected_cluster, selected_namespace

def home_view(request):
    """
    /home
    :param request:
    :return:
    """
    if request.method == 'GET':
        context = {
            'clusters': cluster_views.get_cluster_list_view(),
        }

        if len(context['clusters']['clusters']) > 0:
            selected_cluster = context['clusters']['clusters'][0]
            selected_cluster_name = selected_cluster['name']

        else:
            selected_cluster = cluster_views.get_cluster_view(None)
            selected_cluster_name = None

        # to fill default view cluster records(default: 5)
        context['number_null_records'] = range(number_of_default_view_contents - len(context['clusters']['clusters']))

        context['cluster_details'] = selected_cluster
        selected_cluster_nodes = cluster_views.get_nodes_view(selected_cluster_name)

        context['nodes'] = selected_cluster_nodes
        context['namespaces'] = workload_views.get_namespace_list_view(selected_cluster_name)

        try:
            context['user'] = authorize_user(request)
        except PermissionError:
            error = 'Unauthorized: fail to authorize user account'
            logger.warning(error)
            return redirect('frontend:login')

        return render(request, 'index.html', context)

def pod_view(request):
    """
    workloads > pod renderer
    /pod
    :param request:
    :return:
    """
    selectedCluster = None
    selectedNamespace = None

    if 'selectedCluster' in request.COOKIES:
        selectedCluster = request.COOKIES['selectedCluster']

    if 'selectedNamespace' in request.COOKIES:
        selectedNamespace = request.COOKIES['selectedNamespace']

    cluster_name_list_view = cluster_views.get_cluster_list_view({'filter': 'name'})

    # check whether cluster name is in active cluster
    found = False
    if len(cluster_name_list_view['clusters']) > 0:
        for cluster in cluster_name_list_view['clusters']:
            if cluster['name'] == selectedCluster:
                found = True

        if not found:
            selectedCluster = cluster_name_list_view['clusters'][0]['name']
            selectedNamespace = '_all_'
    else:
        selectedCluster = None

    namespace_list_view = workload_views.get_namespace_list_view(selectedCluster)

    if len(namespace_list_view['namespaces']) <= 0:
        selectedNamespace = None

    if request.method == 'GET':
        context = {
            # fills cluster_data.cluster_list with agent data
            'clusters': cluster_name_list_view,

            # fills pod_data.namespaces_list with agent data
            'namespaces': namespace_list_view,

            # fills pod_data.pod_list with agent data
            'pod_list': workload_views.get_pod_list_view(selectedCluster, selectedNamespace),

            'selectedCluster': selectedCluster,
            'selectedNamespace': selectedNamespace
        }

        context['number_null_records'] = range(5 - len(context['pod_list']['pods']))

        try:
            context['user'] = authorize_user(request)
        except PermissionError:
            error = 'Unauthorized: fail to authorize user account'
            logger.warning(error)
            return redirect('frontend:login')

        response = render(request, 'pod.html', context)
        response.set_cookie('selectedCluster', selectedCluster)
        response.set_cookie('selectedNamespace', selectedNamespace)

        return response


def deployment_view(request):
    """
    /deployment
    :param request:
    :return:
    """
    selectedCluster = None
    selectedNamespace = None

    if 'selectedCluster' in request.COOKIES:
        selectedCluster = request.COOKIES['selectedCluster']

    if 'selectedNamespace' in request.COOKIES:
        selectedNamespace = request.COOKIES['selectedNamespace']

    cluster_name_list_view = cluster_views.get_cluster_list_view({'filter': 'name'})

    # check whether cluster name is in active cluster
    found = False
    if len(cluster_name_list_view['clusters']) > 0:
        for cluster in cluster_name_list_view['clusters']:
            if cluster['name'] == selectedCluster:
                found = True

        if not found:
            selectedCluster = cluster_name_list_view['clusters'][0]['name']
            selectedNamespace = '_all_'
    else:
        selectedCluster = None

    namespace_list_view = workload_views.get_namespace_list_view(selectedCluster)

    if len(namespace_list_view['namespaces']) <= 0:
        selectedNamespace = None

    if request.method == 'GET':
        context = {
            'clusters': cluster_name_list_view,
            'namespaces': namespace_list_view,
            'deployment_list': workload_views.get_deployment_list_view(selectedCluster, selectedNamespace),
            'selectedCluster': selectedCluster,
            'selectedNamespace': selectedNamespace
        }

        context['number_null_records'] = range(number_of_default_view_contents - len(context['deployment_list']['deployments']))

        try:
            context['user'] = authorize_user(request)
        except PermissionError:
            error = 'Unauthorized: fail to authorize user account'
            logger.warning(error)
            return redirect('frontend:login')

        response = render(request, 'deployment.html', context)
        response.set_cookie('selectedCluster', selectedCluster)
        response.set_cookie('selectedNamespace', selectedNamespace)

        return response


def daemonset_view(request):
    """
    /daemonset
    :param request:
    :return:
    """
    selectedCluster = None
    selectedNamespace = None

    if 'selectedCluster' in request.COOKIES:
        selectedCluster = request.COOKIES['selectedCluster']

    if 'selectedNamespace' in request.COOKIES:
        selectedNamespace = request.COOKIES['selectedNamespace']

    cluster_name_list_view = cluster_views.get_cluster_list_view({'filter': 'name'})

    # check whether cluster name is in active cluster
    found = False
    if len(cluster_name_list_view['clusters']) > 0:
        for cluster in cluster_name_list_view['clusters']:
            if cluster['name'] == selectedCluster:
                found = True

        if not found:
            selectedCluster = cluster_name_list_view['clusters'][0]['name']
            selectedNamespace = '_all_'
    else:
        selectedCluster = None

    namespace_list_view = workload_views.get_namespace_list_view(selectedCluster)

    if len(namespace_list_view['namespaces']) <= 0:
        selectedNamespace = None

    if request.method == 'GET':
        context = {
            'clusters': cluster_name_list_view,
            'namespaces': namespace_list_view,
            'daemonset_list': workload_views.get_daemonset_list_view(selectedCluster, selectedNamespace),
            'selectedCluster': selectedCluster,
            'selectedNamespace': selectedNamespace
        }

        context['number_null_records'] = range(
            number_of_default_view_contents - len(context['daemonset_list']['daemonsets']))
        try:
            context['user'] = authorize_user(request)
        except PermissionError:
            error = 'Unauthorized: fail to authorize user account'
            logger.warning(error)
            return redirect('frontend:login')

        response = render(request, 'daemonset.html', context)
        response.set_cookie('selectedCluster', selectedCluster)
        response.set_cookie('selectedNamespace', selectedNamespace)

        return response

def service_view(request):
    """
    /service
    :param request:
    :return:
    """
    selectedCluster = None
    selectedNamespace = None

    if 'selectedCluster' in request.COOKIES:
        selectedCluster = request.COOKIES['selectedCluster']

    if 'selectedNamespace' in request.COOKIES:
        selectedNamespace = request.COOKIES['selectedNamespace']

    cluster_name_list_view = cluster_views.get_cluster_list_view({'filter': 'name'})

    # check whether cluster name is in active cluster
    found = False
    if len(cluster_name_list_view['clusters']) > 0:
        for cluster in cluster_name_list_view['clusters']:
            if cluster['name'] == selectedCluster:
                found = True

        if not found:
            selectedCluster = cluster_name_list_view['clusters'][0]['name']
            selectedNamespace = '_all_'
    else:
        selectedCluster = None

    namespace_list_view = workload_views.get_namespace_list_view(selectedCluster)

    if len(namespace_list_view['namespaces']) <= 0:
        selectedNamespace = None

    if request.method == 'GET':
        context = {
            'clusters': cluster_name_list_view,
            'cluster_details': cluster_views.get_cluster_view(selectedCluster),
            'namespaces': namespace_list_view,
            'service_list': service_views.get_service_list_view(selectedCluster, selectedNamespace),
            'selectedCluster': selectedCluster,
            'selectedNamespace': selectedNamespace

        }

        context['number_null_records'] = range(
            number_of_default_view_contents - len(context['service_list']['services']))

        try:
            context['user'] = authorize_user(request)
        except PermissionError:
            error = 'Unauthorized: fail to authorize user account'
            logger.warning(error)
            return redirect('frontend:login')

        response = render(request, 'service.html', context)
        response.set_cookie('selectedCluster', selectedCluster)
        response.set_cookie('selectedNamespace', selectedNamespace)

        return response

def account_view(request):
    """
    /account
    :param request:
    :return:
    """
    if request.method == 'GET':
        users = User.objects.all()
        user_list = []

        for user in users:
            if not user.is_admin:
                user_list.append({
                    'username': user.username,
                    'name': user.name,
                    'organization': user.organization,
                    'department': user.department,
                    'tel': user.tel,
                    'email': user.email,
                    'ctime': user.date_created
                })
        context = {
            'users': user_list,
            'error': 'no_error'
        }

        try:
            context['user'] = authorize_user(request)
        except PermissionError:
            error = 'Unauthorized: fail to authorize user account'
            logger.warning(error)
            return redirect('frontend:login')
        return render(request, 'account.html', context)


def login_view(request):
    """
    /login
    :param request:
    :return:
    """
    if request.method == 'GET':
        token_key = request.COOKIES.get("token")

        if token_key is None:
            return render(request, 'login.html')

        else:
            if Token.objects.filter(key=token_key).exists():
                token = Token.objects.get(key=token_key)

            else:
                error = 'Unauthorized: fail to authorize user account'
                logger.warning(error)
                return render(request, 'login.html')

            if User.objects.filter(email=token.user).exists():
                return redirect('frontend:index')

            else:
                error = 'Unauthorized: fail to authorize user account'
                logger.warning(error)
                return render(request, 'login.html')
