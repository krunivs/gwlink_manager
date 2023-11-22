import sys

from cache.localhost import Configure
from cache.request_cache import RequestCache
from gwlink_manager import settings
from mqtt.producer import Publisher
from gwlink_migration.scheduler import MigrationScheduler
from repository.cache.cluster import ClusterCache
from utils.memory_manage import MemoryManager

def start():
    # configure runtime
    Configure()

    # start memory manager
    MemoryManager().start()

    # start MQTT publisher
    Publisher().start()

    # start Request Cache
    RequestCache().start()

    # cluster session audit
    ClusterCache().start()

    # start migration scheduler
    MigrationScheduler().start()