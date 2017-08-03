from utils import run_cmd
from utils import enter_depend_test
enter_depend_test()

from depend_test_framework.core import Action, ParamsRequire, Provider, Consumer


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
        params.logger.info("Mock: " + cmd)
        return
    run_cmd(cmd)
