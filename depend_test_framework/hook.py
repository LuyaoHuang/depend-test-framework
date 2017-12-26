"""
Hook module
"""


class BaseHook(object):
    pass


class EnvHook(BaseHook):
    def setup(self, params):
        raise NotImplementedError

    def clean_up(self, params):
        raise NotImplementedError


class CaseHook(BaseHook):
    def setup(self, params, env):
        raise NotImplementedError

    def clean_up(self, params, env):
        raise NotImplementedError
