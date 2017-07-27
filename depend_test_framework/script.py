from engine import Demo
import vm_basic
import migration
import mock_test
from core import Params
from log import get_logger, prefix_logger

LOGGER = get_logger(__name__)

def main():
    d = Demo([vm_basic, migration, mock_test], test_funcs=[mock_test.vcpu_hotplug, mock_test.hot_plug_mem])
    params = Params()
    params.guest_name = 'vm1'
    params.new_vcpu = 10
    params.maxmem = 1024
    params.target_mem = 512
    params.src_host = 'source host'
    params.pretty_display()
    params.mock = True
    d.run(params)

if __name__ == '__main__':
    main()
