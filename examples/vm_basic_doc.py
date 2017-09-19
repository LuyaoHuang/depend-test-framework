from utils import STEPS, RESULT, SETUP
import copy

# TODO: use a class for this
DEFAULT = {
    'memory': 1048576,
    'uuid': 'c156ca6f-3c16-435b-980d-9745e1d84ad1',
    'name': 'vm1',
    'id': 1,
}

def start_guest(params, env):
    """
    Start guest
    """
    params.doc_logger.info(STEPS + "# virsh start %s" % params.guest_name)
    params.doc_logger.info(RESULT + "Domain %s started" % params.guest_name)

    # TODO: move this to another place, since the auto part will need this also
    info = dict(env.get_data('$guest_name.config').data)
    env.set_data('$guest_name.active', info)


def destroy_guest(params, env):
    """
    Destory guest
    """
    params.doc_logger.info(STEPS + "# virsh destroy %s" % params.guest_name)
    params.doc_logger.info(RESULT + "Domain %s destroyed" % params.guest_name)


def define_guest(params, env):
    """
    define a new guest
    """
    params.doc_logger.info(STEPS + "# virsh define %s" % params.guest_xml)
    params.doc_logger.info(RESULT + "Domain %s defined from %s" % (params.guest_name,
                                                                   params.guest_xml))
    info = dict(DEFAULT)
    # TODO: support store mutli domain info
    if params.guest_name:
        info['name'] = params.guest_name
    if params.guest_memory:
        info['memory'] = params.guest_memory
    env.set_data('$guest_name.config', info)


def undefine_guest(params, env):
    """
    undefine guest
    """
    params.doc_logger.info(STEPS + "# virsh undefine %s" % params.guest_name)
    params.doc_logger.info(RESULT + "Domain %s has been undefined" % (params.guest_name))
