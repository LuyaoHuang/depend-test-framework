from utils import enter_depend_test, STEPS, RESULT, SETUP
enter_depend_test()

from depend_test_framework.core import Action, ParamsRequire, Provider, Consumer, CheckPoint, TestObject


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'pagesize'])
@Provider.decorator('hugepage_config', Provider.SET)
def host_hugepage_config(params, env):
    """
    set environment on host
    """
    pass


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'pagesize'])
@Consumer.decorator('$guest_name.config', Consumer.REQUIRE)
@Consumer.decorator('hugepage_config', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE_N)
@Provider.decorator('$guest_name.hugepage', Provider.SET)
def guest_hugepage_settings(params, env):
    """
    set the huegapege xml element in guest xml
    """
    pass


@CheckPoint.decorator(1)
@ParamsRequire.decorator(['guest_name', 'pagesize'])
@Consumer.decorator('hugepage_config', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.hugepage', Consumer.REQUIRE)
def check_hugepage_cmdline(params, env):
    """
    Check the qemu command line
    """
    pass
