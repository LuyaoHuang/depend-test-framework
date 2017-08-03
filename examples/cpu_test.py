"""
Cpu related test
"""

from utils import enter_depend_test, run_cmd
enter_depend_test()

import types
from depend_test_framework.core import Action, CheckPoint

PARAM = {'target_vcpu': types.IntType,}
ENV = {'cpu_status': types.DictType}

@Action.decorator(1)
def vcpu_hotplug(params, env):
    guest = env.guest_name
    if params.get('target_vcpu'):
        target = params.get('target_vcpu')
    else:
        target = random_choose_vcpu(guest)
    run_cmd('virsh setvcpus %s %d --live')

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
    guest = env.guest_name
    load_vcpu_status(guest)

@CheckPoint.decorator(2)
def login_guest_check_vcpu(params, env):
    pass
