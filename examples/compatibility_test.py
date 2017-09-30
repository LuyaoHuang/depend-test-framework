from utils import enter_depend_test, STEPS, RESULT, SETUP
enter_depend_test()

from depend_test_framework.test_object import Action, CheckPoint, TestObject, Mist, MistDeadEndException, MistClearException
from depend_test_framework.dependency import Provider, Consumer
from depend_test_framework.base_class import ParamsRequire


@Action.decorator(1)
@ParamsRequire.decorator(['compatibility'])
@Provider.decorator('libvirt.updated', Provider.SET)
def update_libvirt(params, env):
    """
    """
    pass
