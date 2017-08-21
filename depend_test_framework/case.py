"""
TODO
"""

class Case(object):
    def __init__(self, steps, src_env=None,
                 tgt_env=None, cleanups=None):
        self._steps = steps
        self.step_num = len(steps)
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
