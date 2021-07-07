"""
Classes that help to identify the dependency between test objects
"""
import copy

from .base_class import Entrypoint, check_func_entrys, get_entrypoint

from .log import get_logger

LOGGER = get_logger(__name__)


class Dependency(Entrypoint):
    def __init__(self, env_depend, depend_type):
        self.env_depend = env_depend
        self.depend_list = env_depend.split('.')
        self.type = depend_type

    def __hash__(self):
        return hash("%s|%s" % (self.env_depend, self.type))

    def __eq__(self, target):
        if not isinstance(target, Dependency):
            return False

        if self.env_depend == target.env_depend and self.type == target.type:
            return True
        else:
            return False

    def __repr__(self):
        return "<Dependency depend='%s' type='%s'>" % (self.env_depend, self.type)

    def effect_env(self, env):
        raise NotImplementedError


class Graft(Entrypoint):
    """
    TODO
    """
    def __init__(self, src, tgt):
        self.src = src
        self.tgt = tgt

    def effect_env(self, env):
        sub_env = env.get_data(self.src)
        new_env = copy.deepcopy(sub_env)
        env.set_data(self.tgt, new_env)
        if not new_env.data:
            new_env.data = True

    def gen_trans_depend(self, dep):
        # TODO this is a work around
        if self.src in dep.env_depend:
            return dep.__class__(dep.env_depend.replace(self.src, self.tgt), dep.type)


class Cut(Entrypoint):
    """
    TODO
    """
    def __init__(self, src):
        self.src = src

    def effect_env(self, env):
        sub_env = env.get_data(self.src)
        sub_env.childs = {}
        sub_env.data = False


class Migrate(Graft):
    """
    TODO
    """
    def effect_env(self, env):
        sub_env = env.get_data(self.src)
        new_env = copy.deepcopy(sub_env)
        env.set_data(self.tgt, new_env)
        if sub_env is None:
            # TODO: need do more test on this case
            return
        if not new_env.data:
            new_env.data = True
        sub_env.childs = {}
        sub_env.data = False


class Provider(Dependency):
    CLEAR = "clear"
    SET = "set"

    @classmethod
    def clear(cls, *args, **kwargs):
        ret = super(Provider, cls).decorator(*args, **kwargs)
        return ret

    @classmethod
    def set(cls, *args, **kwargs):
        ret = super(Provider, cls).decorator(*args, **kwargs)
        return ret

    def effect_env(self, env):
        if self.type == self.SET:
            need_set = True
        elif self.type == self.CLEAR:
            need_set = False

        env.set_data(self.env_depend, need_set)


class Consumer(Dependency):
    REQUIRE = "require"
    REQUIRE_N = "require not"

    @classmethod
    def require(cls, *args, **kwargs):
        ret = super(Consumer, cls).decorator(*args, **kwargs)
        return ret

    @classmethod
    def require_n(cls, *args, **kwargs):
        ret = super(Consumer, cls).decorator(*args, **kwargs)
        return ret

    def effect_env(self, env):
        raise Exception


class ExtraDepend(object):
    def __init__(self, function_name, depend_list):
        self.func_name = function_name
        self.depends = set(depend_list)

    def __repr__(self):
        return "<ExtraDepend func_name='%s' at 0x%xd>" % self.func_name


class CustomParams(Entrypoint):
    """ Support user update params dynamically before run cases
        usage:
        @CustomParams.decorator()
        def func_name(params):
            params['new_params'] = 'example'
            return params
    """
    pass


def is_ExtraDepend(obj):
    return isinstance(obj, ExtraDepend)


def is_Graft(obj):
    return check_func_entrys(obj, Graft)


def is_Cut(obj):
    return check_func_entrys(obj, Cut)


def is_CustomParams(obj):
    return check_func_entrys(obj, CustomParams)


def get_all_depend(func, depend_types=None,
                   depend_cls=Dependency, ret_list=True):
    entrys = get_entrypoint(func)
    if not entrys:
        return []
    if ret_list:
        depends = []
    else:
        depends = {}
    for entry in entrys:
        if isinstance(entry, depend_cls):
            if not depend_types or entry.type in depend_types:
                if ret_list:
                    depends.append(entry)
                else:
                    depends.setdefault(entry.env_depend, []).append(entry)
    return depends
