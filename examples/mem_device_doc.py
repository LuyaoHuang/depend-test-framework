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

def verify_memory_device(params, env):
    """
    check memroy device
    """
    pass

def set_maxmemory(params, env):
    """
    Add maxmemory in guest xml for memory device
    """
    params.doc_logger.info(STEPS + """
  <maxMemory slots='%d' unit='KiB'>%d</maxMemory>
        """ % (params.maxmemory.slots, params.maxmemory.size))

def attach_mem_device(params, env):
    """
    Hotplug memory device
    """
    params.doc_logger.info(STEPS + """
    # cat memdev.xml
    <memory model='dimm'>
      <target>
        <size unit='KiB'>%d</size>
        <node>%d</node>
      </target>
    </memory>
        """ % (params.memdevice.size, params.memdevice.node))
    params.doc_logger.info("# virsh attach-device %s memdev.xml --live" % params.guest_name)
    params.doc_logger.info(RESULT + "Device attached successfully")


def detach_mem_device(params, env):
    """
    Hot unplug memory device
    """
    params.doc_logger.info(STEPS + """
    # cat memdev.xml
    <memory model='dimm'>
      <target>
        <size unit='KiB'>%d</size>
        <node>%d</node>
      </target>
    </memory>
        """ % (params.memdevice.size, params.memdevice.node))
    params.doc_logger.info("# virsh detach-device %s memdev.xml --live" % params.guest_name)
    params.doc_logger.info(RESULT + "Device detached successfully")
