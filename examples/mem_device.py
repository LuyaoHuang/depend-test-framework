from utils import enter_depend_test, STEPS, RESULT, SETUP
enter_depend_test()

from depend_test_framework.core import Action, ParamsRequire, Provider, Consumer, CheckPoint, TestObject, Mist, MistDeadEndException, MistClearException


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'memdevice'])
@Consumer.decorator('$guest_name.config.maxmemory', Consumer.REQUIRE)
@Provider.decorator('$guest_name.config.memdevice', Provider.SET)
def set_memory_device(params, env):
    """
    """
    pass


@CheckPoint.decorator(1)
@ParamsRequire.decorator(['guest_name', 'memdevice'])
@Consumer.decorator('$guest_name.active.memdevice', Consumer.REQUIRE)
def verify_memory_device(params, env):
    """
    """
    pass


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'maxmemory'])
@Consumer.decorator('$guest_name.config.numa', Consumer.REQUIRE)
@Provider.decorator('$guest_name.config.maxmemory', Provider.SET)
def set_maxmemory(params, env):
    """
    """
    pass


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'memdevice'])
@Consumer.decorator('$guest_name.active.maxmemory', Consumer.REQUIRE)
@Provider.decorator('$guest_name.active.memdevice', Provider.SET)
def attach_mem_device(params, env):
    """
    """
    pass


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'memdevice'])
@Consumer.decorator('$guest_name.active.maxmemory', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.active.memdevice', Consumer.REQUIRE)
@Provider.decorator('$guest_name.active.memdevice', Provider.CLEAR)
def detach_mem_device(params, env):
    """
    """
    pass

@CheckPoint.decorator(1)
@ParamsRequire.decorator(['guest_name', 'memdevice'])
@Consumer.decorator('$guest_name.config', Consumer.REQUIRE)
def check_mem_device_audit(params, env):
    """
    """
    pass
