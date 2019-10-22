from utils import STEPS, RESULT, SETUP
import copy

# TODO: use a class for this
DEFAULT = {
    'memory': 1048576,
    'uuid': 'c156ca6f-3c16-435b-980d-9745e1d84ad1',
    'name': 'vm1',
    'id': 1,
}

def add_disk(params, env):
    """
    add disk
    """
    guest = params.guest_name
    bus = params.bus
    disk_type = params.disk_type
    driver_type = params.driver_type
    img_name = params.img_name
    img_dir = params.img_dir
    img_path = img_dir + img_name
    xml = "<disk type='%s' device='disk'> \n  <driver name='qemu' type='%s'/> \n "%(disk_type,driver_type)
    if disk_type == "file":
        xml = xml + "<source file='%s'/> \n <target dev='sdc' bus='%s'/> \n </disk> \n"%(img_path,bus)
    elif disk_type == "volume":
        xml = xml + "<source pool='default' volume='%s'/> \n <target dev='sdc' bus='%s'/> \n </disk> \n"%(img_name,bus)

    params.doc_logger.info(STEPS + "prepare a xml file named disk.xml \n %s"%xml)
    params.doc_logger.info(STEPS + "run command \n # virsh attach-device guest-name disk.xml --config")
    params.doc_logger.info(RESULT + "Device attached successfully")

def check_disk(params, env):
    """
    check disk
    """
    params.doc_logger.info(STEPS + "check the disk xml exists in the guest xml and disk exists in this guest")
    params.doc_logger.info(RESULT + "the disk xml exists in the guest xml and disk exists in this guest")
