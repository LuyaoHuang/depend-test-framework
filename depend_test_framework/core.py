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
    return getattr(fn, '_test_entry', None)

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


class MistDeadEndException(Exception):
    """
    This means the mist is end of the road
    """


class MistClearException(Exception):
    """
    This means the mist have been clear
    """


class Mist(object):
    """
    TODO Need explain what's this
    """
    def __init__(self, start, end, func):
        self.start = start
        self.end = end
        self.func = func
        env = Env()
        env.set_from_depends(start)
        self._start_env = env
        env = Env()
        env.set_from_depends(end)
        self._end_env = env

    def reach(self, env, func):
        new_env = env.gen_transfer_env(func)
        if self._start_env <= env and self._end_env <= new_env:
            return True
        else:
            return False

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class Container(set):
    pass

class Params(dict):
    def __getattr__(self, key):
        value = self.get(key)
        if isinstance(value, dict) and not isinstance(value, self.__class__):
            value = self[key] = self.__class__(value)
        return value

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
        strings = ''
        strings += ("=" * 8 + "Parameters" + "=" * 8 + "\n")
        for key, value in self.items():
            strings += ("    Param %s is %s\n" % (key, value))
        strings += ("=" * 20 + "\n")

class Memory(Container):
    pass

class Env(object):
    """
    TODO
    """
    def __init__(self, data=None, parent=None, childs=None, path=''):
        self.data = data
        self.parent = parent
        self.childs = childs if childs else {} 
        self._path = path
#    def __getattr__(self, key):
#        value = self.get(key)
#        if not value and not key.startswith("_"):
#            value = child_env = self.__class__()
#            self[key] = child_env
#        return value

#    def __setattr__(self, key, value):
#        if isinstance(value, self.__class__):
#            self[key] = value
#        else:
#            super(Env, self).__setattr__('_data', value)

    def __getitem__(self, key):
        value = self.childs.get(key)
        if not value and not key.startswith("_"):
            if self._path:
                child_path = '%s.%s' % (self._path, key)
            else:
                child_path = '%s' % key
            value = child_env = self.__class__(parent=self, path=child_path)
            self.childs[key] = child_env
        return value

    def __setitem__(self, key, value):
        if isinstance(value, self.__class__):
            self.childs[key] = value
        else:
            child_env = self[key]
            child_env.data = value

    def __str__(self):
        return self.struct_table()

    def keys(self):
        return self.childs.keys()

    def values(self):
        return self.childs.values()

    def items(self):
        return self.childs.items()

    def get_data(self, path):
        return self._get_data_from_path(path)

    def set_data(self, path, value):
        self._set_data_from_path(path, value)

    def _get_data_from_path(self, path, use_getitem=False):
        if not path:
            return self
        split_path = path.split('.')
        tmp_env = self
        for data in split_path:
            if not isinstance(tmp_env, self.__class__):
                return
            if use_getitem:
                tmp_env = tmp_env[data]
            else:
                tmp_env = tmp_env.childs.get(data)
            if tmp_env is None:
                return
        return tmp_env

    def _set_data_from_path(self, path, value):
        env = self._get_data_from_path(path, True)
        if env is None:
            raise Exception
        env.data = value

    def hit_require(self, depend):
        if depend.type == Consumer.REQUIRE:
            require = True
        elif depend.type == Consumer.REQUIRE_N:
            require = False
        else:
            raise NotImplementedError

        ret = self._get_data_from_path(depend.env_depend)
        if ret:
            return require == bool(ret.data)
        else:
            return not require

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
        return (self.__class__, (self.data, self.parent, self.childs),)

    def __hash__(self):
        """
        NOTICE: don't change the env if really use this
        """
        return hash(self.struct_table())

    def struct_table(self):
        if not self.keys():
            #TODO
            return '{}'
        ret = '{'
        for key, value in sorted(self.items()):
            if value.need_fmt():
                ret += ' %s: %s,' % (key, value.struct_table())
        ret += '}'
        return ret

    def __cmp__(self, target):
        return self.struct_table() == target.struct_table()

    def __eq__(self, target):
        return self.__cmp__(target)

    def __len__(self):
        num = 0
        if self.values():
            for child in self.values():
                num += len(child)
        elif self.data:
            return 1
        return num

    def need_fmt(self):
        for child in self.values():
            if child.need_fmt():
                return True
        if self.data:
            return True
        return False

    def __repr__(self):
        return "<%s path='%s' data='%s'>" % (self.__class__.__name__, self._path, self.data)

    def __le__(self, target):
        return self._check_include(target)

    def __ge__(self, target):
        return target._check_include(self)

    def _check_include(self, target):
        for key, value in self.items():
            if value.data and key not in target.keys():
                return False
            if not value._check_include(target[key]):
                return False
        return True


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
