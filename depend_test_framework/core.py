"""
Core
TODO: Need split
"""
from functools import partial
import types
import copy
from log import get_logger, prefix_logger

LOGGER = get_logger(__name__)


def register_entrypoint(fn, entrypoint):
    descriptors = getattr(fn, '_test_entry', None)

    if descriptors is None:
        descriptors = set()
        setattr(fn, '_test_entry', descriptors)

    descriptors.add(entrypoint)

def get_entrypoint(fn):
    if isinstance(fn, types.FunctionType):
        return getattr(fn, '_test_entry', None)
    try:
        if issubclass(fn, TestObject):
            return getattr(fn, '_test_entry', None)
    except TypeError:
        return

class TestObject(object):
    _test_entry = set()
    def __call__(self, *args, **kwargs):
        """
        Put the real steps in this function
        """
        raise NotImplementedError

class Entrypoint(object):
    __params = None

    def __new__(cls, *args, **kwargs):
        inst = super(Entrypoint, cls).__new__(cls)
        inst.__params = (args, kwargs)
        return inst

    @classmethod
    def decorator(cls, *args, **kwargs):

        def registering_decorator(fn, args, kwargs):
            instance = cls(*args, **kwargs)
            register_entrypoint(fn, instance)
            return fn

        if len(args) == 1 and isinstance(args[0], types.FunctionType):
            # usage without arguments to the decorator:
            # @foobar
            # def spam():
            #     pass
            return registering_decorator(args[0], args=(), kwargs={})
        else:
            # usage with arguments to the decorator:
            # @foobar('shrub', ...)
            # def spam():
            #     pass
            return partial(registering_decorator, args=args, kwargs=kwargs)


class CheckPoint(Entrypoint):
    """
    CheckPoint
    """
    def __init__(self, test_level, version=None):
        self.test_level = test_level
        self.version = version
        self.checkpoints = None

    def bind(self, checkpoints):
        self.checkpoints = checkpoints

    def is_bound(self):
        return True if self.checkpoints else False


class Action(Entrypoint):
    """
    Action
    """
    def __init__(self, test_level, version=None):
        self.test_level = test_level
        self.version = version
        self.actions = None

    def bind(self, actions):
        self.actions = actions

    def is_bound(self):
        return True if self.actions else False


class Hybrid(Entrypoint):
    """
    Action + CheckPoint + ...
    Only work with function have yield 
    """
    def __init__(self, test_level, version=None):
        self.test_level = test_level
        self.version = version
        self.actions = None
        self.checkpoints = None

    def bind(self, actions, checkpoints):
        self.actions = actions
        self.checkpoints = checkpoints

    def is_bound(self):
        return True if self.actions else False


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


class ParamsRequire(Entrypoint):
    def __init__(self, param_depend):
        self.param_depend = Params()
        for key in param_depend:
            self.param_depend[key] = True

class Container(set):
    pass

class Params(dict):
    def __getattr__(self, key):
        if key not in self.keys():
            raise Exception("Cannot find %s in params" % key)
        return self.get(key)

    def __setattr__(self, key, value):
        self[key] = value

    @property
    def key_set(self):
        return set(self.keys())

    def __le__(self, target):
        return self.key_set <= target.key_set

    def __ge__(self, target):
        return self.key_set >= target.key_set

    def __lt__(self, target):
        return self.key_set < target.key_set

    def __gt__(self, target):
        return self.key_set > target.key_set

    def pretty_display(self):
        LOGGER.info("=" * 8 + "Parameters" + "=" * 8)
        for key, value in self.items():
            LOGGER.info("    Param %s is %s" % (key, value))
        LOGGER.info("=" * 20)

class Memory(Container):
    pass

class Env(dict):
    """
    TODO
    """
    def __getattr__(self, key):
        value = self.get(key)
        if not value and not key.startswith("_"):
            value = child_env = self.__class__()
            self[key] = child_env
        return value

    def __setattr__(self, key, value):
        self[key] = value

    def _get_data_from_path(self, path, use_getattr=False):
        if not path:
            return self
        split_path = path.split('.')
        tmp_env = self
        for data in split_path:
            if use_getattr:
                tmp_env = getattr(tmp_env, data, None)
            else:
                tmp_env = tmp_env.get(data)
            if tmp_env is None:
                return
        return tmp_env

    def _set_data_from_path(self, path, value):
        split_path = path.split('.')
        if value is False:
            # TODO
            env = self._get_data_from_path('.'.join(split_path[:-1]))
            if not env or split_path[-1] not in env.keys():
                return
            env.pop(split_path[-1])
            if not env:
                self._set_data_from_path('.'.join(split_path[:-1]), False)
        else:
            env = self._get_data_from_path('.'.join(split_path[:-1]), True)
            env[split_path[-1]] = value

    def hit_require(self, depend):
        if depend.type == Consumer.REQUIRE:
            require = True
        elif depend.type == Consumer.REQUIRE_N:
            require = False
        else:
            raise NotImplementedError

        ret = self._get_data_from_path(depend.env_depend)

        return require == bool(ret)

    def hit_requires(self, depends):
        for depend in depends:
            if not self.hit_require(depend):
                return False

        return True

    def set_from_depends(self, depends):
        for depend in depends:
            self.set_from_depend(depend)

    def set_from_depend(self, depend):
        if depend.type == Provider.SET:
            need_set = True
        elif depend.type == Provider.CLEAR:
            need_set = False
        else:
            return

        self._set_data_from_path(depend.env_depend, need_set)

    def gen_transfer_env(self, func):
        """
        return transfered env Or Null if not suit
        """
        con = get_all_depend(func, depend_cls=Consumer)
        if not self.hit_requires(con):
            return
        new_env = copy.deepcopy(self)
        pro = get_all_depend(func, depend_cls=Provider)
        new_env.set_from_depends(pro)
        return new_env

    @classmethod
    def gen_require_env(cls, func):
        """
        return required env
        """
        cons = get_all_depend(func, depend_cls=Consumer)
        env = cls()
        for con in cons:
            if con.type == Consumer.REQUIRE:
                env._set_data_from_path(con.env_depend, True)
        return env

    def __reduce__(self):
        return self.__reduce_ex__(None)

    def __reduce_ex__(self, protocol):
        return (self.__class__, (self.items(),),)

    def __hash__(self):
        """
        NOTICE: don't change the env if really use this
        """
        return hash(str(self))

def is_TestObject(obj):
    try:
        return issubclass(obj, TestObject)
    except TypeError:
        return

def is_Action(obj):
    return _check_func_entrys(obj, Action)

def is_CheckPoint(obj):
    return _check_func_entrys(obj, CheckPoint)

def is_Hybrid(obj):
    return _check_func_entrys(obj, Hybrid)

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

def get_func_params_require(func):
    entrys = get_entrypoint(func)
    if not entrys:
        return
    for entry in entrys:
        if isinstance(entry, ParamsRequire):
            return entry

def _check_func_entrys(obj, internal_type):
    entrys = get_entrypoint(obj)
    if not entrys:
        return False
    for entry in entrys:
        if isinstance(entry, internal_type):
            return True

    return False
