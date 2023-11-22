from django.db import models

# Create your models here.


class AgentRequestCache(models.Model):

    class RequestStatus(models.TextChoices):
        """
        MQTT Request Status
        """
        NOT_READY = 'not_ready'
        RUNNING = 'running'
        FAILED = 'failed'
        SUCCEEDED = 'succeeded'

    class Method(models.TextChoices):
        """
        MQTT Request Method
        """
        GET = 'GET'
        POST = 'POST'
        DELETE = 'DELETE'
        PUT = 'PUT'
        UNKNOWN = 'UNKNOWN'

    # auto increment
    id = models.BigAutoField(primary_key=True)

    # request_id(uuid4 format)
    request_id = models.CharField(max_length=128,
                                  verbose_name='mqtt request',
                                  unique=True,
                                  null=False)

    # request status
    status = models.CharField(max_length=10,
                              choices=RequestStatus.choices,
                              default=RequestStatus.NOT_READY,
                              verbose_name='request status')

    # request URL
    url = models.CharField(max_length=512,
                           null=True,
                           verbose_name='mqtt request url')
    # request method
    method = models.CharField(max_length=10,
                              choices=Method.choices,
                              default=Method.UNKNOWN,
                              verbose_name='mqtt request method')

    # request date
    request_date = models.TimeField(verbose_name='request date')

    # result
    result = models.CharField(max_length=1024,
                              null=True,
                             verbose_name='mqtt request result')

    # success
    success = models.BooleanField(default=False)

    # error text in response
    error = models.CharField(max_length=512,
                             null=True,
                             verbose_name='mqtt request url')

    # response date
    response_date = models.TimeField(verbose_name='response date',
                                     null=True)

    def __str__(self):
        return self.request_id

    class Meta:
        verbose_name = 'mqtt_request'
        verbose_name_plural = 'mqtt_requests'

