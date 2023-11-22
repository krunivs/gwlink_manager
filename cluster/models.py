from django.db import models


class Cluster(models.Model):
    class Role(models.TextChoices):
        """
        Cluster role in multi-cluster
        """
        LOCAL = 'Local'
        REMOTE = 'Remote'
        NONE = 'None'

    class MultiClusterConfigState(models.TextChoices):
        """
        MultiClusterConfigState
        """
        CONNECTING = 'Connecting'
        CONNECTED = 'Connected'
        DISCONNECT_PENDING = 'DisconnectPending'
        DISCONNECTING = 'Disconnecting'
        NONE = 'None'

    # auto increment
    id = models.BigAutoField(primary_key=True)

    # request_id(uuid4 format)
    cluster_id = models.CharField(max_length=128,
                                  verbose_name='cluster id',
                                  unique=True,
                                  null=False)
    # cluster name
    cluster_name = models.CharField(max_length=128,
                                    verbose_name='cluster name',
                                    unique=True,
                                    null=False)
    # cluster description
    description = models.CharField(max_length=512,
                                   null=True,
                                   verbose_name='cluster description')
    # registration command
    registration_command = models.CharField(max_length=2048,
                                            null=True,
                                            verbose_name='agent registration command')
    # multi-cluster connect id(uuid4 format)
    mc_connect_id = models.CharField(max_length=128,
                                     default=None,
                                     null=True,
                                     verbose_name='multicluster connection id')

    # cluster role in multi-cluster
    role = models.CharField(max_length=10,
                            choices=Role.choices,
                            default=Role.NONE,
                            verbose_name='cluster role in multi-cluster')

    # multi-cluster config state
    mc_config_state = models.CharField(max_length=20,
                                       choices=MultiClusterConfigState.choices,
                                       default=MultiClusterConfigState.NONE,
                                       verbose_name='multi-cluster config state')

    # broker-info.subm
    broker_info = models.CharField(max_length=2048,
                                   null=True,
                                   verbose_name='broker info file')

    # broker-info.subm update date
    broker_info_update_date = models.TimeField(verbose_name='broker-info.subm update date',
                                               null=True)
    # create date
    create_date = models.TimeField(verbose_name='create date',
                                   null=False, auto_now=True)
    # update date
    update_date = models.TimeField(verbose_name='update date',
                                   null=False, auto_now=True)

    def __str__(self):
        return self.cluster_id

    class Meta:
        verbose_name = 'cluster'
        verbose_name_plural = 'clusters'
