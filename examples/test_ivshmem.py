from utils import enter_depend_test, STEPS, RESULT, SETUP
enter_depend_test()

from depend_test_framework.core import Action, ParamsRequire, Provider, Consumer, CheckPoint, TestObject, Mist, MistDeadEndException, MistClearException


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'ivshmem'])
@Consumer.decorator('$guest_name.config', Consumer.REQUIRE)
@Provider.decorator('$guest_name.config.ivshmem', Provider.SET)
def set_ivshmem_device(params, env):
    """
    """
    pass

@CheckPoint.decorator(2)
@ParamsRequire.decorator(['guest_name', 'ivshmem'])
@Consumer.decorator('$guest_name.active.ivshmem', Consumer.REQUIRE)
def check_ivshmem_in_guest(params, env):
    pass

@CheckPoint.decorator(1)
@ParamsRequire.decorator(['guest_name', 'ivshmem'])
@Consumer.decorator('$guest_name.active.ivshmem', Consumer.REQUIRE)
def check_ivshmem_cmdline(params, env):
    pass

@CheckPoint.decorator(1)
@ParamsRequire.decorator(['guest_name', 'ivshmem'])
@Consumer.decorator('$guest_name.config.ivshmem', Consumer.REQUIRE)
def check_ivshmem_audit(params, env):
    pass
