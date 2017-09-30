from utils import enter_depend_test, STEPS, RESULT, SETUP
enter_depend_test()

from depend_test_framework.core import Action, ParamsRequire, Provider, Consumer, CheckPoint, TestObject, Mist, MistDeadEndException, MistClearException


def set_ivshmem_device(params, env):
    """
    Add the ivshmem device in guest xml
    """
    if params.ivshmem.model != 'ivshmem-plain':
        raise NotImplementedError
    params.doc_logger.info(STEPS + """
    # cat ivshmem.xml
    <shmem name='%s'>
      <model type='%s'/>
      <size unit='KiB'>%d</size>
    </shmem>
        """ % (params.ivshmem.name,
               params.ivshmem.model,
               params.ivshmem.size if params.ivshmem.size else 4096))

    if '/' in params.ivshmem.name:
        start = [Provider('$guest_name.active', Provider.CLEAR),
                  Provider('$guest_name.active.ivshmem', Provider.CLEAR)]
        end = [Provider('$guest_name.active.ivshmem', Provider.SET)]

        start2 = [Provider('$guest_name.active', Provider.SET),
                  Provider('$guest_name.active.ivshmem', Provider.CLEAR)]
        end2 = [Provider('$guest_name.active.ivshmem', Provider.SET)]

        def use_invald_ivshmem_name(name, func, params, env):
            """
            Guest should fail to start with a invalid ivshmem device
            """
            if name == 'start':
                params.doc_logger.info(STEPS + "# virsh start %s", params.guest_name)
                params.doc_logger.info(RESULT + """
        error: Failed to start domain %s
        error: unsupported configuration: shmem name '%s' must not contain '/'
                """ % (params.guest_name, params.ivshmem.name))
            elif name == 'attach':
                params.doc_logger.info(STEPS + "# virsh attach-device %s ivshmem.xml --live", params.guest_name)
                params.doc_logger.info(RESULT + """
        error: Failed to attach device from ivshmem.xml
        error: unsupported configuration: shmem name '%s' must not contain '/'
                """ % params.ivshmem.name)
            raise MistDeadEndException

        return Mist({"start": (start, end), "attach": (start2, end2)}, use_invald_ivshmem_name)

def check_ivshmem_cmdline(params, env):
    """
    check qemu command line:

    """
    params.doc_logger.info(STEPS + "# ps aux|grep %s" % params.guest_name)
    params.doc_logger.info(RESULT + """
...
-object memory-backend-file,id=shmmem-shmem0,mem-path=/dev/shm/%s,size=%d,share=yes -device ivshmem-plain,id=shmem0,memdev=shmmem-shmem0
...
""" % (params.ivshmem.name, params.ivshmem.size if params.ivshmem.size else 4194304))

def check_ivshmem_in_guest(params, env):
    """
    Verify the ivshmem device function in guest
    """
    params.doc_logger.info(STEPS + "TODO")
    params.doc_logger.info(RESULT + "TODO")

def check_ivshmem_audit(params, env):
    """
    Check the audit system
    """
    params.doc_logger.info(STEPS + "Make sure the auditd is running")

    start1 = [Provider('$guest_name.active', Provider.SET),
              Provider('$guest_name.active.ivshmem', Provider.CLEAR)]
    end1 = [Provider('$guest_name.active.ivshmem', Provider.SET)]

    start2 = [Provider('$guest_name.active', Provider.CLEAR),
              Provider('$guest_name.active.ivshmem', Provider.CLEAR)]
    end2 = [Provider('$guest_name.active.ivshmem', Provider.SET)]

    start3 = [Provider('$guest_name.active.ivshmem', Provider.SET)]
    end3 = [Provider('$guest_name.active.ivshmem', Provider.CLEAR),
            Provider('$guest_name.active', Provider.SET)]

    def check_audit_log(name, func, params, env):
        """
        Check the audit log
        """
        func(params, env)

        active_info = env.get_data('$guest_name.active').data
        params.doc_logger.info("")
        params.doc_logger.info(STEPS + "# ausearch -m VIRT_RESOURCE -ts recent")
        params.doc_logger.info(RESULT + """
...
type=VIRT_RESOURCE ... msg='virt=kvm resrc=shmem reason=%s vm="%s" uuid=%s size=%d path=/dev/shm/%s exe="/usr/sbin/libvirtd" hostname=? addr=? terminal=? res=success'
...
        """ % (name, active_info.get('name'),
               active_info.get('uuid'),
               params.ivshmem.size if params.ivshmem.size else 4194304,
               params.ivshmem.name,))

    return Mist({"attach": (start1, end1), "start": (start2, end2), "detach": (start3, end3)}, check_audit_log)

def hot_plug_ivshmem(params, env):
    """
    Hot plug a ivshmem device
    """
    params.doc_logger.info("ivshmem.xml:")
    params.doc_logger.info("""
    <shmem name='%s'>
      <model type='%s'/>
      <size unit='KiB'>%d</size>
    </shmem>
        """ % (params.ivshmem.name,
               params.ivshmem.model,
               params.ivshmem.size if params.ivshmem.size else 4096))
    params.doc_logger.info(STEPS + "# virsh attach-device %s ivshmem.xml --live" % params.guest_name)
    params.doc_logger.info(RESULT + "Device attached successfully")

def hot_unplug_ivshmem(params, env):
    """
    Hot unplug ivshmem device
    """
    params.doc_logger.info("ivshmem.xml:")
    params.doc_logger.info("""
    <shmem name='%s'>
      <model type='%s'/>
      <size unit='KiB'>%d</size>
    </shmem>
        """ % (params.ivshmem.name,
               params.ivshmem.model,
               params.ivshmem.size if params.ivshmem.size else 4096))
    params.doc_logger.info(STEPS + "# virsh detach-device %s ivshmem.xml --live" % params.guest_name)
    params.doc_logger.info(RESULT + "Device detached successfully")
