from utils import enter_depend_test, STEPS, RESULT, SETUP
enter_depend_test()

from depend_test_framework.core import Action, ParamsRequire, Provider, Consumer, CheckPoint, TestObject, Mist, MistDeadEndException, MistClearException


def set_memory_device(params, env):
    """
    Add memory device in guest xml
    """
    params.doc_logger.info(STEPS + """
        <memory model='dimm'>
          <target>
            <size unit='KiB'>%d</size>
            <node>0</node>
          </target>
        </memory>
        """ % params.memdevice.size)

def verify_memory_device(parms, env):
    """
    check memroy device
    """
    pass
