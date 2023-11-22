from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.home_view, name='index'),
    path('home', views.home_view, name='home'),
    path('pod', views.pod_view, name='pod'),
    path('deployment', views.deployment_view, name='deployment'),
    path('daemonset', views.daemonset_view, name='daemonset'),
    path('service', views.service_view, name='service'),
    path('account', views.account_view, name='account'),
    path('login', views.login_view, name='login')
]
