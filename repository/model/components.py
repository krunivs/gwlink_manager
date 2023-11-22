import six

from repository.common.type import Kubernetes, ActiveStatus, PodStatus, Constraints
from repository.model.k8s.condition import Condition
from utils.validate import Validator


class Component:
    """
    Cedge Cluster Components model class
    """
    fields = {
        'kind': 'kind',
        'name': 'str',
        'namespace': 'str',
        'valid': 'bool',
        'constraints': 'Constraints',
        'resource_type': 'str',
        'conditions': 'list[Condition]',
    }

    def __init__(self, name=None, namespace=None, resource_type=None, constraints=None):
        """
        Components()
        """
        self.kind = Kubernetes.COMPONENTS.value
        self.name = name
        self.namespace = namespace
        self.valid = False
        self.resource_type = resource_type
        self.constraints = constraints
        self.conditions = []

    def set_name(self, val):
        """
        setter
        :param val: (str) resource name(i.e., pod name, service name)
        :return:
        """
        if not Validator.is_str(val):
            raise ValueError('Invalid val({}). Must input str'.format(val))
        self.name = val

    def get_name(self):
        """
        getter
        :return: (str) resource name(i.e., pod name, service name)
        """
        return self.name

    def set_namespace(self, val):
        """
        setter
        :param val: (str) namespace
        :return:
        """
        if not Validator.is_str(val):
            raise ValueError('Invalid val({}). Must input str'.format(val))
        self.namespace = val

    def get_namespace(self):
        """
        getter
        :return: (str) namespace
        """
        return self.namespace

    def set_resource_type(self, val):
        """
        setter
        :param val: (str) resource type (Kubernetes(Enum)'s value)
        :return:
        """
        if not Kubernetes.value(val):
            raise ValueError('Invalid val({}). Must input Kubernetes(Enum) value'.format(val))
        self.resource_type = val

    def get_resource_type(self):
        """
        getter
        :return: (str) resource type (Kubernetes(Enum)'s value)
        """
        return self.resource_type

    def set_valid(self, val):
        """
        setter
        :param val: (bool) True - valid False - invalid
        :return:
        """

        if val is None or type(val) != bool:
            raise ValueError('Invalid val({}). Must input bool'.format(val))

        self.valid = val

    def get_status(self):
        """
        getter
        :return: (bool) True - valid False - invalid
        """
        return self.valid

    def set_conditions(self, val):
        """
        setter
        :param val: (list[Condition])
        :return:
        """
        if val is None:
            raise TypeError('val is None. Must input val as list[Condition] type')
        if type(val) != list:
            raise TypeError('Invalid val type({}). Must input val as list[Condition] type'.format(type(val)))
        for item in val:
            if type(item) != Condition:
                raise TypeError('Invalid val type({}). Must input val as list[Condition] type'.format(type(item)))
        self.conditions = val

    def set_constraints(self, val):
        """
        setter
        :param val: (Constraints(Enum))
        :return:
        """
        if val is None or not Constraints.validate():
            raise ValueError('Invalid val(({}){}). Input Constraints(Enum) value'.format(type(val), val))

        self.constraints = val

    def get_constraints(self):
        """
        getter
        :return: (Constraints(Enum))
        """
        return self.constraints

    def get_conditions(self):
        """
        getter
        :return: (list[Condition])
        """
        return self.conditions

    def to_dict(self):
        """Returns the model properties as a dict"""
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

        instance = cls()
        conditions = []

        for key, value in _dict.items():
            if key == 'conditions':
                for item in value:  # list(Condition)
                    conditions.append(Condition.to_object(item))
                setattr(instance, key, conditions)
            else:
                setattr(instance, key, value)

        return instance
