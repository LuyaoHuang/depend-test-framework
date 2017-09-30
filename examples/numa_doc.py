from utils import enter_depend_test, STEPS, RESULT, SETUP
enter_depend_test()

from depend_test_framework.test_object import Mist, MistDeadEndException, MistClearException
from depend_test_framework.dependency import Provider, Consumer


def set_guest_numa(params, env):
    """
    Add numa element in guest xml
    """
    numa_xml = ''
    for i, n in enumerate(params.numa):
        numa_xml += "      <cell id='%d' cpus='%s' memory='%s' unit='KiB'/>" % (i, n.cpus, n.memory)

    params.doc_logger.info(STEPS + """
  <cpu>
    <numa>
%s
    </numa>
  </cpu>
        """ % numa_xml)

