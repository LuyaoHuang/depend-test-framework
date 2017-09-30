"""
A class help to create and manage a virtual test env
"""
import contextlib
import copy

from log import get_logger
from dependency import Consumer, Provider, Cut, Graft, get_all_depend

LOGGER = get_logger(__name__)


class Env(object):
    """
    TODO
    """
    def __init__(self, data=None, parent=None, childs=None, path=''):
        self.data = data
        self.parent = parent
        self.childs = childs if childs else {}
        self._path = path

        self._record = False
        self._history = []

    def __getitem__(self, key):
        value = self.childs.get(key)
        if value is None and not key.startswith("_"):
            value = child_env = self.__class__(parent=self, path=key)
            self.childs[key] = child_env
        return value

    def __setitem__(self, key, value):
        if isinstance(value, self.__class__):
            self.childs[key] = value
            value.parent = self
        else:
            child_env = self[key]
            child_env.data = value

    @contextlib.contextmanager
    def record(self):
        self._history = []
        self._record = True
        yield
        self._record = False

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
        LOGGER.debug('Env %s set_data, path: %s, value: %s', self, path, value)
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
        if isinstance(value, self.__class__):
            env.childs = value.childs
            env._change_parent(env)
            LOGGER.debug('Env %s update sub env: %s, value: %s', self, path, value)
            env.data = value.data
        else:
            LOGGER.debug('Env %s update sub env %s, data %s -> %s', self, path, env.data, value)
            env.data = value

    def _change_parent(self, tgt):
        for child in self.childs.values():
            child.parent = tgt

    def hit_require(self, depend):
        if depend.type == Consumer.REQUIRE:
            require = True
        elif depend.type == Consumer.REQUIRE_N:
            require = False
        else:
            raise NotImplementedError

        ret = self._get_data_from_path(depend.env_depend)
        if ret is not None and (ret.struct_table() != '{}' or ret.data):
            return require
        else:
            return not require

    def hit_requires(self, depends):
        for depend in depends:
            if not self.hit_require(depend):
                return False

        return True

    def call_effect_env(self, objs):
        for obj in objs:
            obj.effect_env(self)

    def gen_transfer_env(self, func):
        """
        return transfered env Or Null if not suit
        """
        con = get_all_depend(func, depend_cls=Consumer)
        if not self.hit_requires(con):
            return
        new_env = copy.deepcopy(self)
        objs = get_all_depend(func, depend_cls=(Provider, Graft, Cut))
        new_env.call_effect_env(objs)
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
        return (self.__class__, (self.data, self.parent, self.childs, self._path),)

    def __hash__(self):
        """
        NOTICE: don't change the env if really use this
        """
        return hash(self.struct_table())

    def struct_table(self):
        if not self.keys():
            # TODO
            return '{}'
        ret = '{'
        for key, value in sorted(self.items()):
            if value.need_fmt():
                ret += ' %s|%s: %s,' % (key, bool(value.data), value.struct_table())
        ret += '}'
        return ret

    def __cmp__(self, target):
        if not isinstance(target, self.__class__):
            return False
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

    def _full_path(self):
        if self.parent is not None and self.parent._full_path():
            return '%s.%s' % (self.parent._full_path(), self._path)
        return self._path

    def __repr__(self):
        return "<%s path='%s' data='%s'>" % (self.__class__.__name__,
                                             self._full_path(), self.data)

    def __le__(self, target):
        return self._check_include(target)

    def __ge__(self, target):
        return target._check_include(self)

    def _check_include(self, target):
        for key, value in self.items():
            # TODO: any possible to make this looks more correct ?
            # if not value.childs:
            if value.data and (key not in target.keys() or not target[key].data):
                return False
            if value.data is False and key in target.keys() and target[key].data:
                return False
            if not value._check_include(target[key]):
                return False
        return True
