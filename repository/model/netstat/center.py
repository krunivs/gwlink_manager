import six
from repository.common.type import ConnectionStatus, NetStat


class CenterNetwork:
    """
    Center network model class
    """

    fields = {
        'kind': 'str',
        'name': 'str',          # center network name(http access url)
        'status': 'str',        # network status(i.e., 'connected' or 'unavailable')
        'http': 'str',          # http access '/' url
        'https': 'str',         # https access '/' url
        'amqp': 'str',          # amqp access url
        'token': 'str',         # center http/https access token
    }

    def __init__(self, name):
        """
        MultiClusterNetwork()
        :param name: (str) cedge-center access '/' url(http or https)
        """
        self.kind = NetStat.CENTER_NETWORK.value
        self.name = name
        self.status = ConnectionStatus.UNAVAILABLE.value
        self.http = None
        self.https = None
        self.amqp = None
        self.token = None

    @classmethod
    def validate_dict(cls, _dict):
        """
        validate _dict
        """
        for key in _dict.keys():
            if key not in cls.fields.keys():
                raise KeyError('Invalid key({})'.format(key))

    @classmethod
    def to_object(cls, _dict):
        """
        Returns the model object
        """
        cls.validate_dict(_dict)

        instance = cls(name=_dict['name'])
        instance.set_status(_dict['status'])

        return instance

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}
        for attr, _ in six.iteritems(self.fields):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        return result

    def set_status(self, val):
        """
        setter
        :param val: (str)
        :return:
        """
        if not ConnectionStatus.validate(val):
            raise TypeError('Invalid Enum type(value={}). '
                            'Must input val as str type in ConnectionStatus(Enum)'.format(val))
        self.status = val

    def get_status(self):
        """
        getter
        :return: (str)
        """
        return self.status

    def set_http(self, val):
        """
        setter
        :param val: (str)
        :return:
        """
        if type(val) != str:
            raise TypeError('Invalid input type({}). Must input str as val'.format(type(val)))
        self.http = val

    def get_http(self):
        """
        getter
        :return: (str)
        """
        return self.http

    def set_https(self, val):
        """
        setter
        :param val: (str); nullable
        :return:
        """

        if val is not None and type(val) != str:
            raise TypeError('Invalid input type({}). Must input str as url'.format(val))
        self.https = val

    def get_https(self):
        """
        getter
        :return: (str)
        """
        return self.https

    def set_amqp(self, val):
        """
        setter
        :param val: (str); nullable
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid input type({}). Must input str as val'.format(val))
        self.amqp = val

    def get_amqp(self):
        """
        getter
        :return: (str)
        """
        return self.amqp

    def set_token(self, val):
        """
        setter
        :param val: (str); nullable
        :return:
        """
        if val is not None and type(val) != str:
            raise TypeError('Invalid input type({}). Must input str as val'.format(val))
        self.token = val

    def get_token(self):
        """
        getter
        :return: (str)
        """
        return self.token


