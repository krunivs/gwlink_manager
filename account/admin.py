from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoAdmin
from django.contrib.auth.models import Group

from account.models import User


class UserAdmin(DjangoAdmin):
  list_display = ('email', 'username', 'date_created', 'last_login', 'is_admin', 'is_staff')
  search_fields = ('email', 'username',)
  readonly_fields = ('date_created', 'last_login')

  filter_horizontal = ()
  list_filter = ()
  fieldsets = ()


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
