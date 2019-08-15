"""
Some base classes
"""
import types
from functools import partial

from .log import get_logger

LOGGER = get_logger(__name__)


def register_entrypoint(fn, entrypoint):
    descriptors = getattr(fn, '_test_entry', None)

    if descriptors is None:
        descriptors = set()
        setattr(fn, '_test_entry', descriptors)

    descriptors.add(entrypoint)


def get_entrypoint(fn):
    return getattr(fn, '_test_entry', None)


def check_func_entrys(obj, internal_type):
    entrys = get_entrypoint(obj)
    if not entrys:
        return False
    for entry in entrys:
        if isinstance(entry, internal_type):
            return True

    return False


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


class Container(set):
    def imap(self, func_name, *args, **kwargs):
        for obj in self:
            func = getattr(obj, func_name)
            func(*args, **kwargs)


class ParamsRequire(Entrypoint):
    def __init__(self, param_depend):
        self.param_depend = Params()
        for key in param_depend:
            self.param_depend[key] = True


class Params(dict):
    def __getattr__(self, key):
        value = self.get(key)
        if isinstance(value, dict) and not isinstance(value, self.__class__):
            value = self[key] = self.__class__(value)
        elif isinstance(value, list):
            value = [self.__class__(i) for i in value]
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


def get_func_params_require(func):
    entrys = get_entrypoint(func)
    if not entrys:
        return
    for entry in entrys:
        if isinstance(entry, ParamsRequire):
            return entry
