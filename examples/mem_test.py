from utils import enter_depend_test
enter_depend_test()

from depend_test_framework.core import Action, ParamsRequire, Provider, Consumer, CheckPoint, TestObject


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'pagesize'])
@Provider.decorator('hugepage_config', Provider.SET)
def host_hugepage_config(params, env):
    """
    set environment on host
    """
    return
    if params.hugetlbfs_mount is not '':
        params.doc_logger.info("""
            Then guest memory backing files will be put in %s/libvirt/qemu/.
            #mount -t hugetlbfs hugetlbfs %s 

            2> reserve memory for huge pages, e.g:
            #sysctl vm.nr_hugepages=600
            """ % (params.hugetlbfs_mount, params.hugetlbfs_mount))
    else:
        start = [Provider('$guest_name.active', Provider.CLEAR),
                 Provider('$guest_name.hugepage', Provider.SET)]
        end = [Provider('$guest_name.active', Provider.SET),
               Provider('$guest_name.hugepage', Provider.SET)]
        def mist_host_hugepage(func, params, env):
            try:
                func(params, env)
            except:
                # TODO: check the failed reason
                if params.hugetlbfs_mount is '':
                    return env
        return Mist(start, end, mist_host_hugepage)


@Action.decorator(1)
@ParamsRequire.decorator(['guest_name', 'pagesize'])
@Consumer.decorator('$guest_name.config', Consumer.REQUIRE)
@Consumer.decorator('hugepage_config', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE_N)
@Provider.decorator('$guest_name.hugepage', Provider.SET)
def guest_hugepage_settings(params, env):
    """
    set the huegapege xml element in guest xml
    """
    pass


@CheckPoint.decorator(1)
@ParamsRequire.decorator(['guest_name', 'pagesize'])
@Consumer.decorator('hugepage_config', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.active', Consumer.REQUIRE)
@Consumer.decorator('$guest_name.hugepage', Consumer.REQUIRE)
def check_hugepage_cmdline(params, env):
    """
    Check the qemu command line
    """
    pass
