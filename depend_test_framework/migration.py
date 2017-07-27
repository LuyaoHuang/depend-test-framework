from utils import run_cmd
from core import Action, ParamsRequire, Provider, Consumer

from log import get_logger, prefix_logger

LOGGER = get_logger(__name__)

@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'target_host'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Consumer.decorator('$target_host.$guest_name.active', Consumer.REQUIRE_N)
@Provider.decorator('$target_host.$guest_name.active', Provider.SET)
@Provider.decorator('$guest_name.active', Provider.CLEAR)
def migrate(params, env):
    target = params.target_host
    guest_name = params.guest_name
    cmd = 'virsh migrate %s qemu+ssh://%s/system --live' % (guest_name, target)
    if params.mock:
        LOGGER.info("Mock: " + cmd)
        return
    run_cmd(cmd)
