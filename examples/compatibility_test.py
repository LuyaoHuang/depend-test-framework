from utils import enter_depend_test, STEPS, RESULT, SETUP
enter_depend_test()

from depend_test_framework.core import Action, ParamsRequire, Provider, Consumer, CheckPoint, TestObject, Mist, MistDeadEndException, MistClearException


@Action.decorator(1)
@ParamsRequire.decorator(['compatibility'])
@Provider.decorator('libvirt.updated', Provider.SET)
def update_libvirt(params, env):
    """
    """
    pass
