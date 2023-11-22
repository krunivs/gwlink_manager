from django.db import models

# Create your models here.
from gwlink_migration.common.type import MigrationStatus, MigrationError


class MigrationRequest(models.Model):
    class Role(models.TextChoices):
        """
        Cluster role in multi-cluster
        """
        LOCAL = 'Local'
        REMOTE = 'Remote'
        NONE = 'None'

    # migration id
    id = models.CharField(primary_key=True,
                          max_length=128,
                          verbose_name='migration id',
                          unique=True,
                          null=False)

    # source cluster name
    source_cluster_name = models.CharField(max_length=128,
                                           verbose_name='source cluster name',
                                           unique=False,
                                           null=False)

    # source cluster role
    source_cluster_role = models.CharField(max_length=10,
                            choices=Role.choices,
                            default=Role.NONE,
                            verbose_name='cluster role in multi-cluster')

    # delete origin
    delete_origin = models.BooleanField(default=False,
                                        verbose_name='delete origin pod')

    # source namespace
    source_namespace = models.CharField(max_length=128,
                                        verbose_name='source namespace',
                                        unique=False,
                                        null=True)

    # source pod
    source_pod = models.CharField(max_length=128,
                                  verbose_name='source pod',
                                  unique=False,
                                  null=False)

    # target cluster name
    target_cluster_name = models.CharField(max_length=128,
                                           verbose_name='target cluster name',
                                           unique=False,
                                           null=False)

    # target node name(hostname)
    target_node_name = models.CharField(max_length=128,
                                        verbose_name='target node name',
                                        unique=False,
                                        null=False)

    # migration status
    status = models.CharField(default=MigrationStatus.ISSUED.value,
                              max_length=32,
                              verbose_name='migration status',
                              unique=False,
                              null=False)

    # sub task execution order
    last_subtask_seq = models.IntegerField(default=0,
                                           verbose_name='current executing subtask sequence')

    # total number of sub-task
    number_of_subtask = models.IntegerField(default=0,
                                            verbose_name='number of total subtask')

    # issued date(timestamp string)
    issued_date = models.CharField(max_length=50,
                                   verbose_name='issued date(timestamp)',
                                   null=False)
    # start date(timestamp string)
    start_date = models.CharField(max_length=50,
                                  verbose_name='start date(timestamp)',
                                  null=True)

    # end date(timestamp)
    end_date = models.CharField(max_length=50,
                                verbose_name='end date(timestamp)',
                                null=True)

    # updated date(timestamp)
    updated_date = models.CharField(max_length=50,
                                    verbose_name='update date(timestamp)',
                                    null=True)


    def __str__(self):
        return 'id={}, src_cls={}, target_cls={}, target_node={}, ns={}, pod={}, seq={}/{}, status={}'.format(
            self.id,
            self.source_cluster_name,
            self.target_cluster_name,
            self.target_node_name,
            self.source_namespace,
            self.source_pod,
            self.number_of_subtask,
            self.last_subtask_seq,
            self.status)

    class Meta:
        verbose_name = 'migration_request'
        verbose_name_plural = 'migration_requests'


class MigrationTask(models.Model):
    # auto increment
    id = models.BigAutoField(primary_key=True)

    # foreign key
    migration_request = models.ForeignKey(MigrationRequest, on_delete=models.CASCADE)

    # task name
    task = models.CharField(max_length=128,
                            verbose_name='task name',
                            unique=False,
                            null=False)

    # status
    status = models.CharField(default=MigrationStatus.ISSUED.value,
                              max_length=32,
                              verbose_name='task status',
                              unique=False,
                              null=False)

    # error
    error = models.CharField(default=MigrationError.NONE.value,
                             max_length=32,
                             verbose_name='migration error',
                             unique=False,
                             null=True)

    # error reason
    reason = models.CharField(max_length=512,
                              verbose_name='error message',
                              unique=False,
                              null=True)

    # current retry count
    retry = models.IntegerField(default=0,
                                verbose_name='retry count')

    # task sequence
    sequence = models.IntegerField(default=0,
                                   verbose_name='task sequence number')

    # issued date
    issued_date = models.CharField(max_length=50,
                                   verbose_name='issue date(timestamp)',
                                   null=False)

    # task start date
    start_date = models.CharField(max_length=50,
                                  verbose_name='start date(timestamp)',
                                  null=True)

    # task completed date
    end_date = models.CharField(max_length=50,
                                verbose_name='end date(timestamp)',
                                null=True)

    def __str__(self):
        return 'id={}, task={}, seq={}, issue={}, start={}, end={}, status={}, retry={}'.format(
            self.id,
            self.task,
            self.sequence,
            self.issued_date,
            self.start_date,
            self.end_date,
            self.status,
            self.retry)

    class Meta:
        verbose_name = 'migration_task'
        verbose_name_plural = 'migration_tasks'