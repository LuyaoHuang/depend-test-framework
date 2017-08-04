"""
Cpu related test
"""

from utils import enter_depend_test, run_cmd
enter_depend_test()

import types
from depend_test_framework.core import Action, CheckPoint, TestObject, ParamsRequire, Consumer

PARAM = {'target_vcpu': types.IntType,}
ENV = {'cpu_status': types.DictType}

def random_choose_vcpu(guest, live=True, higher=True):
    cpu_status = load_vcpu_status(guest)

def load_vcpu_status(guest):
    cpu_status = {}
    out = run_cmd('virsh vcpucount ' + guest)
    for line in out.splitlines():
        tmp = line.split()
        if len(tmp) != 3:
            continue
        typ, stat, num = tmp
        cpu_status.setdefault(typ, {}).setdefault(stat, num)
    return cpu_status

@CheckPoint.decorator(1)
def check_vcpu_number(params, env):
    # load_vcpu_status(guest)
    params.logger.info('check if need check vcpu')
    tmp = env.get_data('$guest_name.active')
    if tmp and isinstance(tmp.data, dict) and tmp.data.get('cpus'):
        params.logger.info(tmp.data.get('cpus'))

@CheckPoint.decorator(2)
def login_guest_check_vcpu(params, env):
    pass


class vcpu_hotplug_r(TestObject):
    """Hot plug/unplug guest vcpu"""
    _test_entry = set([Action(1),
                       ParamsRequire(['guest_name', 'cpu_plug']),
                       Consumer('$guest_name.active', Consumer.REQUIRE)])

    def __call__(self, params, env):
        assert params.guest_name
        if params.cpu_plug == 'up':
            tmp_env = env.get_data('$guest_name.active')
            if not tmp_env.data or not isinstance(tmp_env.data, dict):
                tmp_env.data = {}
            tmp_env.data['cpus'] = 10
            params.logger.info('set guest vcpus to 10')
            # add CPU
        elif params.cpu_plug == 'down':
            tmp_env = env.get_data('$guest_name.active')
            if not tmp_env.data or not isinstance(tmp_env.data, dict):
                tmp_env.data = {}
            tmp_env.data['cpus'] = 5
            params.logger.info('set guest vcpus to 5')
            # del CPU


class vcpu_coldplug(TestObject):
    """Cold plug/unplug guest vcpu"""
    _test_entry = set([Action(1),
                       ParamsRequire(['guest_name'])])

    def __call__(self, params, env):
        assert params.guest_name
        params.logger.info("change vcpu in guest xml")
