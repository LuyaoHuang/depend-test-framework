from utils import enter_depend_test, STEPS, RESULT, SETUP
enter_depend_test()

from depend_test_framework.core import Action, ParamsRequire, Provider, Consumer, CheckPoint, TestObject, Mist, MistDeadEndException

def host_hugepage_config(params, env):
    """
    set environment on host
    """
    if params.hugetlbfs_mount is None:
        params.hugetlbfs_mount = '/dev/hugepages'

    params.doc_logger.info(SETUP + '# cat /etc/libvirt/qemu.conf\n' + \
                               'hugetlbfs_mount = "%s"\n' % params.hugetlbfs_mount)
    params.doc_logger.info("""
        # service libvirtd restart
        Stopping libvirtd daemon: [ OK ]
        Starting libvirtd daemon: [ OK ]
        """)
    if params.hugetlbfs_mount is not '':
        params.doc_logger.info("""
            Then guest memory backing files will be put in %s/libvirt/qemu/.
            #mount -t hugetlbfs hugetlbfs %s 

            2> reserve memory for huge pages, e.g:
            #sysctl vm.nr_hugepages=600
            """ % (params.hugetlbfs_mount, params.hugetlbfs_mount))
    else:
        # We need do some other things after env reached or require
        start = [Provider('$guest_name.active', Provider.CLEAR),
                 Provider('$guest_name.hugepage', Provider.SET)]
        end = [Provider('$guest_name.active', Provider.SET),
               Provider('$guest_name.hugepage', Provider.SET)]
        def mist_host_hugepage(func, params, env):
            params.doc_logger.info(STEPS + "# virsh start %s" % params.guest_name)
            params.doc_logger.info(RESULT + "error: Failed to start domain %s\nerror: internal error hugepages are disabled by administrator config" % params.guest_name)
            raise MistDeadEndException()
        return Mist(start, end, mist_host_hugepage)


def guest_hugepage_settings(params, env):
    """
    set the huegapege xml element in guest xml
    """
    if params.pagesize == 'default':
        xml = """
              <memoryBacking>
              <hugepages/>
              </memoryBacking>
              """
    elif params.pagesize:
        xml = """
        <memoryBacking>
        <hugepages>
        <page size='%s' unit='KiB'/>
        </hugepages>
        </memoryBacking>
        """ % params.pagesize 
    params.doc_logger.info(STEPS + """
        Add the below xml in guest:
        %s
        """ % xml)


def check_hugepage_cmdline(params, env):
    """
    Check the qemu command line
    """
    params.doc_logger.info(STEPS + "# ps aux|grep %s" % params.guest_name)
    params.doc_logger.info(RESULT + "...-mem-path %s/libvirt/qemu..." % params.hugetlbfs_mount)
