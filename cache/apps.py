import os
from django.apps import AppConfig

from cache import operator


class CacheConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cache'

    def ready(self):
        # Below code help to initialize cedge-agent object only once
        if not os.environ.get('APP'):
            os.environ['APP'] = 'True'
        else:
            operator.start()