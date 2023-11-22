from gwlink_manager import settings


class ComponentCache:
    """
    Component status management class
    """

    def __init__(self):
        self._logger = settings.get_logger(__name__)
        self._conditions = []
        self.clear()

    def clear(self):
        self._conditions = []

    def set_conditions(self, conditions: list):
        """
        set conditions
        :param conditions: (list(Condition))
        :return:
        """
        if conditions is not None:
            if type(conditions) == list:
                if self._conditions:
                    self._conditions = None

                self._conditions = conditions
        return

    def get_conditions(self):
        """
        get component conditions
        :return: (list[Condition])
        """
        return self._conditions

    def _get_condition_object(self, key):
        """
        get condition object for key
        :param key: (str)
        :return:
        """
        for condition in self._conditions:
            if condition.get_condition() == key:
                return condition

        return None

    def print_cluster_component_conditions(self):
        """
        print cluster component conditions
        :return:
        """
        self._logger.debug('')
        self._logger.debug('------------------------------------------------------------')
        for condition in self._conditions:
            self._logger.debug('{}: {}: {}'.format(
                condition.get_condition(), condition.get_status(), condition.get_message()))
        self._logger.debug('------------------------------------------------------------')
        self._logger.debug('')

    def _is_ready_cedge_namespace(self):
        """
        check whether etri namespace is available
        :return: (bool)
        """
        key = 'ETRINamespaceCreated'
        condition = self._get_condition_object(key)
        if condition.get_status() == 'True':
            return True

        return False

    def _is_submariner_components_cleaned(self):
        """
        check whether submariner broker-joined component are cleaned up
        :return: (bool) True - cleaned, False - not cleaned
        """
        keys = ['SubmarinerGatewayReady',
                'SubmarinerGlobalnetReady',
                'SubmarinerRouteAgentReady',
                'SubmarinerLighthouseAgentReady',
                'SubmarinerLighthouseCoreDnsReady']

        for key in keys:
            if self._get_condition_object(key).get_status() == 'True':
                return False

        return True

    def _is_submariner_broker_components_available(self):
        """
        check whether all submariner broker components are available
        :return:
        """
        keys = [
            'SubmarinerNamespaceCreated',
            'SubmarinerOperatorReady']

        for key in keys:
            if self._get_condition_object(key).get_status() == 'False':
                return False

        return True

    def _is_submariner_join_components_available(self):
        """
        check whether all submariner join components are available
        :return:
        """
        keys = ['SubmarinerGatewayReady',
                'SubmarinerGlobalnetReady',
                'SubmarinerRouteAgentReady',
                'SubmarinerLighthouseAgentReady',
                'SubmarinerLighthouseCoreDnsReady']

        for key in keys:
            if self._get_condition_object(key).get_status() == 'False':
                return False

        return True

    def _is_submariner_join_components_creating(self):
        """
        check whether submariner join components are creating or not
        :return:
        """
        keys = ['SubmarinerGatewayReady',
                'SubmarinerGlobalnetReady',
                'SubmarinerRouteAgentReady',
                'SubmarinerLighthouseAgentReady',
                'SubmarinerLighthouseCoreDnsReady']

        for key in keys:
            if self._get_condition_object(key).get_message() == ExecutionStatus.CREATING.value:
                return True

        return False

