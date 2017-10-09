"""
Helpers which help handle the runner result and extend the runner function
"""

import itertools
import contextlib

from case import Case
from test_object import MistClearException
from log import get_logger

LOGGER = get_logger(__name__)


class MistsHandler(object):
    def __init__(self, engine):
        self._engine = engine
        self._mists_c = None
        self._last_mist = None

    def _test_logger(self, *args, **kwargs):
        use_doc = kwargs.get('use_doc', False)
        # FIXME: not only info
        if use_doc:
            self._engine.params.doc_logger.info(*args)
        else:
            self._engine.params.logger.info(*args)

    @contextlib.contextmanager
    def start_handle(self):
        self._mists_c = MistsContainer()
        yield
        self._mists_c = None

    @contextlib.contextmanager
    def watch_func(self):
        self._last_mist = None
        yield

    def gen_extra_cases(self, old_case, src_env=None, test_func=None):
        if not self._last_mist:
            return []
        return list(self._gen_mist_cases(self._last_mist, old_case, src_env, test_func))

    def desc_logger(self, func, use_doc=False):
        if func.__doc__:
            self._test_logger("Desciption: %s" % func.__doc__, use_doc=use_doc)

    def _check_mists(self, mists, env, func, new_env=None):
        # TODO support mutli mist
        if not mists:
            return
        for mist in mists:
            name = mist.reach(env, func, new_env)
            if name:
                return name, mist

    def handle_func(self, func, doc_func,
                    new_env=None, only_doc=True):
        mists = self._mists_c
        tgt_env = new_env or self._engine.env
        params = self._engine.params
        test_func = doc_func if only_doc else func

        mist = self._check_mists(mists, self._engine.env, func, new_env)
        LOGGER.debug("Func %s mist %s", test_func, mist)
        LOGGER.debug("Env: %s", tgt_env)
        if mist:
            name, mist_func = mist
            self.desc_logger(mist_func, only_doc)
            # TODO: here will raise a exception which require the caller handle this
            try:
                mist_func(name, test_func, params, tgt_env)
            except MistClearException:
                mists.remove(mist_func)
            # TODO: mist in the mist
            new_mist = None
        else:
            self.desc_logger(test_func, only_doc)

            new_mist = test_func(params, tgt_env)

        if new_mist and mists is not None:
            LOGGER.debug('Add a new mist %s', new_mist)
            mists.append(new_mist)
            self._last_mist = new_mist

    def _gen_mist_cases(self, mist, old_case, src_env=None, test_func=None):
        # Here we get a new mist in the test func
        # we need to trigger this mist
        if not src_env:
            src_env = self._engine.env
        history_steps = Case(list(old_case.steps),
                             tgt_env=old_case.tgt_env,
                             cleanups=old_case.cleanups)
        if test_func:
            history_steps.append(test_func)

        for name, extra_step in self.find_mist_routes(mist, src_env):
            new_case = history_steps + extra_step
            LOGGER.debug("create a new case: %s", list(new_case.steps))
            LOGGER.debug("history steps: %s, extra_step: %s",
                         list(history_steps.steps), list(extra_step.steps))
            yield name, new_case

    def find_mist_routes(self, mist, src_env=None):
        routes = []
        if src_env is None:
            src_env = self._engine.env

        case_gen = self._engine.case_gen
        for name, data in mist._areas.items():
            start_env, end_env = data
            for tgt_start_env in case_gen.find_suit_envs(start_env, 20):
                if tgt_start_env == src_env:
                    cases = None
                else:
                    cases = case_gen.compute_route_permutations(src_env, tgt_start_env)
                    if not cases:
                        continue
                for tgt_end_env in case_gen.dep_graph[tgt_start_env].keys():
                    if end_env <= tgt_end_env:
                        funcs = case_gen.dep_graph[tgt_start_env][tgt_end_env]
                        if cases:
                            for data in itertools.product(cases, funcs):
                                case = list(data[0])
                                case.append(data[1])
                                case_obj = Case(case, tgt_env=tgt_end_env)
                                yield name, case_obj
                        else:
                            for func in funcs:
                                case_obj = Case([func], tgt_env=tgt_end_env)
                                yield name, case_obj

class MistsContainer(list):
    """
    A list to store the mist
    """
