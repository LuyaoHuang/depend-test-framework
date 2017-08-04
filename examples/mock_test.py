from utils import enter_depend_test
enter_depend_test()

from depend_test_framework.core import Action, ParamsRequire, Provider, Consumer, CheckPoint, TestObject


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'new_vcpu'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
def vcpu_hotplug(params, env):
    assert params.guest_name
    assert params.new_vcpu
    params.logger.info('hotplug vcpu to %d' % params.new_vcpu)


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'maxmem'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE_N)
@Consumer.decorator('$guest_name.config', Consumer.REQUIRE)
@Provider.decorator('$guest_name.have_maxmem', Provider.SET)
def set_maxmem_xml(params, env):
    assert params.guest_name
    assert params.maxmem
    params.logger.info('set %s maxmem to %d' % (params.guest_name, params.maxmem))


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'maxmem'])
@Consumer.decorator('$guest_name.config', Consumer.REQUIRE)
@Provider.decorator('$guest_name.have_maxmem', Provider.CLEAR)
def rm_maxmem_xml(params, env):
    assert params.guest_name
    assert params.maxmem
    params.logger.info('remove %s maxmem in xml' % (params.guest_name))


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'target_mem'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.have_maxmem', Consumer.REQUIRE)
def hot_plug_mem(params, env):
    assert params.guest_name
    assert params.target_mem
    params.logger.info('set running guest %s mem to %d' % (params.guest_name, params.target_mem))


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'src_host', 'disable'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE_N)
@Provider.decorator('$guest_name.active', Provider.SET)
def migrate_guest(params, env):
    assert params.guest_name
    assert params.src_host
    params.logger.info('migrate running guest %s from "%s" to this test env' % (params.guest_name, params.src_host))

@CheckPoint.decorator(1)
@ParamsRequire.decorator(['guest_name'])
def check_mem_from_xml(params, env):
    assert params.guest_name
    params.logger.info("Checking guest memory in xml")


@CheckPoint.decorator(2)
@ParamsRequire.decorator(['guest_name'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
def check_mem_in_guest(params, env):
    assert params.guest_name
    params.logger.info("Checking guest cpu in guest")


class check_vcpu_info(TestObject):
    """check vcpu infomation from guest xml"""
#    def __init__(self):
#        self._test_entry.add(CheckPoint(1))
#        self._test_entry.add(ParamsRequire(['guest_name']))
#        self._test_entry.add(Consumer('$guest_name.active', Consumer.REQUIRE))
    _test_entry = set([CheckPoint(1),
        ParamsRequire(['guest_name']),
        Consumer('$guest_name.active',
                 Consumer.REQUIRE)])

    def __call__(self, params, env):
        assert params.guest_name
        params.logger.info("Checking guest cpu info from xml")
