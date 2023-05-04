import subprocess
import time
import re
import os
import sys
import paramiko

STEPS = "Step:"
RESULT = "Result:"
SETUP = "Setup:"

def enter_depend_test():

    # Simple magic for using scripts within a source tree
    BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.isdir(os.path.join(BASEDIR, 'depend_test_framework')):
        os.environ['PATH'] += ":" + os.path.join(BASEDIR, 'examples')
        sys.path.insert(0, BASEDIR)

def run_cmd(cmd):
    return subprocess.check_output(cmd.split())


def _get_guest_ip(guest_name):
    # TODO: fallback to agent
    ret = run_cmd("virsh -q domifaddr --source lease %s" % guest_name)
    match = re.search(r"([\S]+)$", ret)
    if not match:
        return
    return match.group(1).split("/")[0]


def login_guest_run(guest_name, cmd, passwd, retry=10):
    """
    return stdout string and stderr string
    """
    guest_ip = None
    i = 0
    while not guest_ip:
        i += 1
        guest_ip = _get_guest_ip(guest_name)
        if not guest_ip:
            time.sleep(5)
        if i == retry:
            raise Exception("Time out: %s cmd: %s" % (guest_name, cmd))

    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(guest_ip, username="root", password=passwd)
        _, stdout, stderr = client.exec_command(cmd)
        return stdout.read(), stderr.read()
    finally:
        client.close()
