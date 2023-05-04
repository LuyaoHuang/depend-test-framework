from utils import enter_depend_test, run_cmd
enter_depend_test()

from depend_test_framework.test_object import Action, CheckPoint, TestObject, Mist, MistDeadEndException, MistClearException
from depend_test_framework.dependency import Provider, Consumer, Graft, Cut
from depend_test_framework.base_class import ParamsRequire


PARAM = {}
ENV = {}


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name'])
# Guest should be active(running or paused) and persistent
#@Consumer.decorator('$guest_name.active', Consumer.REQUIRE_N)
@Consumer.decorator('$guest_name.config', Consumer.REQUIRE)
@Provider.decorator('$guest_name.config.vdisk', Provider.SET)
def add_disk(params, env):
    """
    test:add disk
    """
    guest = params.guest_name
    bus = params.bus
    disk_type = params.disk_type
    driver_type = params.driver_type
    img_name = params.img_name
    img_dir = params.img_dir
    img_path = img_dir + img_name


    ret = run_cmd("qemu-img create %s 10M -f %s"%(img_path,driver_type)) 
    params.logger.info("test:the result of creating img is %s"%ret)
    xml = "<disk type='%s' device='disk'>  <driver name='qemu' type='%s'/> "%(disk_type,driver_type)
    if disk_type == "file":
        xml = xml + "<source file='%s'/> <target dev='sdc' bus='%s'/> </disk>"%(img_path,bus)
    elif disk_type == "volume":
        xml = xml + "<source pool='default' volume='%s'/> <target dev='sdc' bus='%s'/> </disk>"%(img_name,bus)
        ret = run_cmd("virsh pool-refresh default")
    else:
        params.logger.info("error: can not gererate the correct xml")
    params.logger.info("test:the xml is %s"%xml)
    f = open('disk.xml', 'w')
    f.write(xml)
    f.close()
    ret = run_cmd("virsh attach-device %s disk.xml --config"%guest)
    params.logger.info("test:the attach result is %s"%ret)

@CheckPoint.decorator(1)
@ParamsRequire.decorator(['guest_name'])
@Consumer.decorator('$guest_name.active.vdisk', Consumer.REQUIRE)
def check_disk(params, env):
    """
    test:check disk
    """
    guest = params.guest_name
    img_name = params.img_name
    img_dir = params.img_dir
    img_path = img_dir + img_name
    ret = run_cmd("virsh dumpxml %s"%guest)
    params.logger.info("test:check result:\n %s"%ret)
    if img_name in ret:
        params.logger.info("check:the disk is in the guest --  pass")
    else:
        params.logger.info("check:the disk is not in the guest --  failed")
    ret = run_cmd("rm -rf %s"%img_path)
    params.logger.info("test:delete the used img %s"%ret)
