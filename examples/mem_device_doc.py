from utils import enter_depend_test, STEPS, RESULT, SETUP
enter_depend_test()

from depend_test_framework.core import Provider, Consumer, Mist, MistDeadEndException, MistClearException


def set_memory_device(params, env):
    """
    Add memory device in guest xml
    """
    params.doc_logger.info(STEPS + """
        <memory model='dimm'>
          <target>
            <size unit='KiB'>%d</size>
            <node>%s</node>
          </target>
        </memory>
        """ % (params.memdevice.size, params.memdevice.node))
    info = env.get_data('$guest_name.config').data
    info['memory'] += params.memdevice.size

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
    info = env.get_data('$guest_name.config').data
    info['maxmemory'] = dict(params.maxmemory)

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

    info = env.get_data('$guest_name.active').data
    info['memory'] += params.memdevice.size


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

    info = env.get_data('$guest_name.active').data
    info['memory'] -= params.memdevice.size

def check_mem_device_audit(params, env):
    """
    Check the audit system
    """
    params.doc_logger.info(STEPS + "Make sure the auditd is running")

    start1 = [Provider('$guest_name.active', Provider.SET),
              Provider('$guest_name.active.memdevice', Provider.CLEAR)]
    end1 = [Provider('$guest_name.active.memdevice', Provider.SET)]

    start2 = [Provider('$guest_name.active', Provider.CLEAR),
              Provider('$guest_name.active.memdevice', Provider.CLEAR)]
    end2 = [Provider('$guest_name.active.memdevice', Provider.SET)]

    start3 = [Provider('$guest_name.active.memdevice', Provider.SET)]
    end3 = [Provider('$guest_name.active.memdevice', Provider.CLEAR),
            Provider('$guest_name.active', Provider.SET)]

    def check_mem_audit_log(name, func, params, env):
        """
        Check the memory device audit log
        """
        if name is not 'start':
            old_mem = env.get_data('$guest_name.active').data.get('memory')
        else:
            old_mem = 0
        func(params, env)

        active_info = env.get_data('$guest_name.active').data
        new_mem = active_info.get('memory')
        params.doc_logger.info("")
        params.doc_logger.info(STEPS + "# ausearch -m VIRT_RESOURCE -ts recent")
        params.doc_logger.info(RESULT + """
...
type=VIRT_RESOURCE ... msg='virt=kvm resrc=mem reason=%s vm="%s" uuid=%s old-mem=%d new-mem=%d exe="/usr/sbin/libvirtd" hostname=? addr=? terminal=? res=success'
...
        """ % ('start' if name is 'start' else 'update',
               active_info.get('name'),
               active_info.get('uuid'), old_mem, new_mem))

    return Mist({"attach": (start1, end1),
                 "start": (start2, end2),
                 "detach": (start3, end3)},
                check_mem_audit_log)


def check_maxmemory(params, env):
    """
    Check maxmemory qemu cmdline
    """
    active_info = env.get_data('$guest_name.active').data
    mem = active_info.get('memory')
    max_mem = active_info.get('maxmemory')
    params.doc_logger.info(STEPS + "# ps aux|grep qemu")
    params.doc_logger.info(RESULT + "-m size=%dk,slots=%d,maxmem=%dk",
                           mem, max_mem['slots'], max_mem['size'])
