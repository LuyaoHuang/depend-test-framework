from utils import STEPS, RESULT, SETUP

def host_hugepage_config(params, env):
    """
    set environment on host
    """
    params.doc_logger.info(SETUP + '\n#mkdir /dev/hugepages\n' + \
                               'Or # cat /etc/libvirt/qemu.conf\n' + \
                               'hugetlbfs_mount = "/dev/hugepages"\n')
    params.doc_logger.info("""
        # service libvirtd restart
        Stopping libvirtd daemon: [ OK ]
        Starting libvirtd daemon: [ OK ]
        Then guest memory backing files can be found in /dev/hugepages/libvirt/qemu/.
        #mount -t hugetlbfs hugetlbfs /dev/hugepages
        2> reserve memory for huge pages, e.g:
        #sysctl vm.nr_hugepages=600
        """)


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
    params.doc_logger.info(RESULT + "...-mem-path /dev/hugetest/libvirt/qemu...")
