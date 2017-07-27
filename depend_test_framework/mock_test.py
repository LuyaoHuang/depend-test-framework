from core import Action, ParamsRequire, Provider, Consumer, CheckPoint
from log import get_logger, prefix_logger

LOGGER = get_logger(__name__)

@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'new_vcpu'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
def vcpu_hotplug(params, env):
    assert params.guest_name
    assert params.new_vcpu
    with prefix_logger(LOGGER, "\033[94mActions:\033[0m"):
        LOGGER.info('hotplug vcpu to %d' % params.new_vcpu)


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'maxmem'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE_N)
@Provider.decorator('$guest_name.have_maxmem', Provider.SET)
def set_maxmem_xml(params, env):
    assert params.guest_name
    assert params.maxmem
    with prefix_logger(LOGGER, "\033[94mActions:\033[0m"):
        LOGGER.info('set %s maxmem to %d' % (params.guest_name, params.maxmem))


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'target_mem'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.have_maxmem', Consumer.REQUIRE)
def hot_plug_mem(params, env):
    assert params.guest_name
    assert params.target_mem
    with prefix_logger(LOGGER, "\033[94mActions:\033[0m"):
        LOGGER.info('set running guest %s mem to %d' % (params.guest_name, params.target_mem))


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'src_host'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE_N)
@Provider.decorator('$guest_name.active', Provider.SET)
def migrate_guest(params, env):
    assert params.guest_name
    assert params.src_host
    with prefix_logger(LOGGER, "\033[94mActions:\033[0m"):
        LOGGER.info('migrate running guest %s from "%s" to this test env' % (params.guest_name, params.src_host))

@CheckPoint.decorator(1)
@ParamsRequire.decorator(['guest_name'])
def check_mem_from_xml(params, env):
    assert params.guest_name
    with prefix_logger(LOGGER, "\033[94mCheckpoints:\033[0m"):
        LOGGER.info("Checking guest memory in xml")


@CheckPoint.decorator(2)
@ParamsRequire.decorator(['guest_name'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
def check_mem_in_guest(params, env):
    assert params.guest_name
    with prefix_logger(LOGGER, "\033[94mCheckpoints:\033[0m"):
        LOGGER.info("Checking guest cpu in guest")
