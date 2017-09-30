from utils import enter_depend_test, STEPS, RESULT, SETUP
enter_depend_test()

from depend_test_framework.core import Provider, Consumer, Mist, MistDeadEndException, MistClearException


def update_libvirt(params, env):
    """
    upgrade libvirt packages
    """
    # TODO: how to make sure the old libvirt is the old version
    params.doc_logger.info(STEPS + """
    update libvirt version to %s:
    yum update libvirt*%s*
""" % (params.compatibility.new_ver, params.compatibility.new_ver,))
