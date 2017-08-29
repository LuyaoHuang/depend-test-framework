"""
TODO
"""
import copy

class Case(object):
    def __init__(self, steps, src_env=None,
                 tgt_env=None, cleanups=None):
        self._steps = steps
        self.src_env = src_env
        self.tgt_env = tgt_env
        if cleanups:
            self.cleanups = Case(cleanups)
        else:
            self.cleanups = None

    def _check_cls(self, tgt):
        if not isinstance(tgt, self.__class__):
            raise Exception("%s is not a %s" % (tgt, self.__class__))

    def __le__(self, tgt):
        self._check_cls(tgt)
        return self.step_num <= tgt.step_num

    def __ge__(self, tgt):
        self._check_cls(tgt)
        return self.step_num >= tgt.step_num

    def __lt__(self, tgt):
        self._check_cls(tgt)
        return self.step_num < tgt.step_num

    def __gt__(self, tgt):
        self._check_cls(tgt)
        return self.step_num > tgt.step_num

    def append(self, step, new_tgt=None):
        if new_tgt is not None:
            self.tgt_env = new_tgt
        self._steps.append(step)

    def __add__(self, tgt):
        if not isinstance(tgt, self.__class__):
            raise Exception('Cannot add a %s obj to %s' % (type(tgt), self.__class__))
        if self.tgt_env != tgt.src_env:
            raise Exception('Env is not match')
        new_obj = self.__class__(list(self._steps), self.src_env, tgt.tgt_env, tgt.cleanups)
        new_obj._steps.extend(tgt._steps)
        return new_obj

    @property
    def step_num(self):
        return len(self._steps)

    @property
    def steps(self):
        for step in self._steps:
            yield step

    @property
    def clean_ups(self):
        if not self.cleanups:
            return

        for step in self.cleanups.steps:
            yield step
