from utils import run_cmd
from core import Action, ParamsRequire, Provider, Consumer
from log import get_logger, prefix_logger

LOGGER = get_logger(__name__, prefix="\033[94mActions:\033[0m")

PARAM = {}
ENV = {}


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE_N)
@Provider.decorator('$guest_name.active', Provider.SET)
def start_guest(params, env):
    guest = params.guest_name
    cmd = 'virsh start ' + guest
    if params.mock:
        LOGGER.info("Mock: " + cmd)
        return
    run_cmd(cmd)


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name'])
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Provider.decorator('$guest_name.active', Provider.CLEAR)
def destroy_guest(params, env):
    guest = params.guest_name
    cmd = 'virsh destroy ' + guest
    if params.mock:
        LOGGER.info("Mock: " + cmd)
        return
    run_cmd(cmd)
