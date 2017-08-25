from utils import enter_depend_test, STEPS, RESULT, SETUP
enter_depend_test()

from depend_test_framework.core import Action, ParamsRequire, Provider, Consumer, CheckPoint, TestObject, Mist, MistDeadEndException, MistClearException


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'memdevice'])
@Consumer.decorator('$guest_name.config', Consumer.REQUIRE)
#@Consumer.decorator('$guest_name.numa_conf', Consumer.REQUIRE)
@Provider.decorator('$guest_name.config.memdevice', Provider.SET)
def set_memory_device(params, env):
    """
    """
    pass


@CheckPoint.decorator(1)
@ParamsRequire.decorator(['guest_name', 'memdevice'])
@Consumer.decorator('$guest_name.active.memdevice', Consumer.REQUIRE)
def verify_memory_device(parms, env):
    """
    """
    pass
