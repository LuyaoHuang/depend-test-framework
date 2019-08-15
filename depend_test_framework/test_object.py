"""
Test object related class
"""
from .base_class import Entrypoint, check_func_entrys
from .env import Env

from .log import get_logger

LOGGER = get_logger(__name__)


class TestObject(object):
    _test_entry = set()
    def __call__(self, *args, **kwargs):
        """
        Put the real steps in this function
        """
        raise NotImplementedError


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


class TestEndException(Exception):
    """ this exception means test end
    """


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
    def __init__(self, area, func, doc_func=None):
        self.func = func
        self.doc_func = doc_func
        self._areas = {}
        for name, data in area.items():
            self.add_area_env(name, *data)

    def add_area_env(self, name, start, end):
        env = Env()
        env.call_effect_env(start)
        start_env = env
        env = Env()
        env.call_effect_env(end)
        end_env = env
        self._areas[name] = (start_env, end_env)

    def reach(self, env, func, new_env=None):
        if not new_env:
            new_env = env.gen_transfer_env(func)
        for name, data in self._areas.items():
            start_env, end_env = data
            LOGGER.debug('Start env: %s End env: %s env: %s New env: %s', start_env, end_env, env, new_env)
            if start_env <= env and end_env <= new_env:
                return name

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    @classmethod
    def issubclass(cls, obj):
        if cls == obj:
            # Don't use this class directly
            return False
        try:
            return issubclass(obj, cls)
        except TypeError:
            return False


class StaticMist(Mist):
    _area = dict()
    active = True
    _doc_func = None

    def __init__(self):
        super(StaticMist, self).__init__(self._area, self.custom_func, self._doc_func)

    def custom_func(self):
        raise NotImplementedError


def is_TestObject(obj):
    try:
        return issubclass(obj, TestObject)
    except TypeError:
        return


def is_Action(obj):
    return check_func_entrys(obj, Action)


def is_CheckPoint(obj):
    return check_func_entrys(obj, CheckPoint)


def is_Hybrid(obj):
    return check_func_entrys(obj, Hybrid)
