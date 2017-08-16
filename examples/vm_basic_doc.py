from utils import STEPS, RESULT, SETUP


def start_guest(params, env):
    """
    Start guest
    """
    params.doc_logger.info(STEPS + "# virsh start %s" % params.guest_name)
    params.doc_logger.info(RESULT + "Domain %s started" % params.guest_name)


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


def undefine_guest(params, env):
    """
    undefine guest
    """
    params.doc_logger.info(STEPS + "# virsh undefine %s" % params.guest_name)
    params.doc_logger.info(RESULT + "Domain %s has been undefined" % (params.guest_name))
