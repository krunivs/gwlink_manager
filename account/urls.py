from django.urls import path

from account import views

app_name = 'account'

api_version = 'v1'

urlpatterns = [
  path(api_version +
       "/users", views.registration_and_list_view, name='register_and_list'),

  path(api_version +
       "/users/<str:username>", views.details_delete_and_update_view, name='delete'),

  path(api_version +
       "/login", views.login_view, name='login'),

  path(api_version +
       "/logout", views.logout_view, name='logout'),
]
