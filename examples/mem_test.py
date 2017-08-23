from utils import enter_depend_test
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


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name'])
@Consumer.decorator('$guest_name.config', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE_N)
@Provider.decorator('$guest_name.mlock', Provider.SET)
def set_mem_lock_xml(params, env):
    """
    """
    pass


@CheckPoint.decorator(1)
@ParamsRequire.decorator(['guest_name'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.mlock', Consumer.REQUIRE)
def verify_mem_lock(params, env):
    pass


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name'])
@Consumer.decorator('$guest_name.config', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE_N)
@Provider.decorator('$guest_name.nosharepage', Provider.SET)
def set_nosharepage_xml(params, env):
    """
    """
    pass


@CheckPoint.decorator(1)
@ParamsRequire.decorator(['guest_name'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.nosharepage', Consumer.REQUIRE)
def verify_nosharepage(params, env):
    pass


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'memtune'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Provider.decorator('$guest_name.memtune', Provider.SET)
def virsh_memtune(params, env):
    """
    """
    pass


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'memtune'])
@Consumer.decorator('$guest_name.config', Consumer.REQUIRE)
@Provider.decorator('$guest_name.memtune_conf', Provider.SET)
def virsh_memtune_conf(params, env):
    """
    """
    pass

@CheckPoint.decorator(1)
@ParamsRequire.decorator(['guest_name', 'memtune'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.memtune', Consumer.REQUIRE)
def verify_memtune_cgroup(params, env):
    """
    """
    pass

@CheckPoint.decorator(1)
@ParamsRequire.decorator(['guest_name', 'memtune'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.memtune', Consumer.REQUIRE)
def verify_memtune_xml(params, env):
    """
    """
    pass

@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'memballoon'])
@Consumer.decorator('$guest_name.config', Consumer.REQUIRE)
@Provider.decorator('$guest_name.memballoon', Provider.SET)
def set_memballoon_xml(params, env):
    """
    """
    pass

@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'curmem'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Provider.decorator('$guest_name.curmem', Provider.SET)
def hot_set_guest_mem(params, env):
    pass

@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'curmem'])
@Consumer.decorator('$guest_name.config', Consumer.REQUIRE)
@Provider.decorator('$guest_name.curmem_conf', Provider.SET)
def cold_set_guest_mem(params, env):
    pass

@CheckPoint.decorator(2)
@ParamsRequire.decorator(['guest_name', 'curmem'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.curmem', Consumer.REQUIRE)
def verify_setmem_in_guest(params, env):
    """
    """
    pass

@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'mem_period'])
@Consumer.decorator('$guest_name.config', Consumer.REQUIRE)
@Provider.decorator('$guest_name.mem_period_conf', Provider.SET)
def virsh_set_period_conf(params, env):
    """
    """
    pass

@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'mem_period'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Provider.decorator('$guest_name.mem_period', Provider.SET)
def virsh_set_period(params, env):
    """
    """
    pass

@CheckPoint.decorator(1)
@ParamsRequire.decorator(['guest_name'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
def virsh_dommemstat(params, env):
    """
    """
    pass

@CheckPoint.decorator(1)
@ParamsRequire.decorator(['guest_name'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.mem_period', Consumer.REQUIRE)
def check_period_in_xml(params, env):
    """
    """
    pass
