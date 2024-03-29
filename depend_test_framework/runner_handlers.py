"""
Helpers which help handle the runner result and extend the runner function
"""

import itertools
import contextlib
import traceback

from .test_object import MistClearException, TestEndException, StaticMist, MistDeadEndException, is_TestObject, ObjectFailedException
from .case import Case
from .log import get_logger

LOGGER = get_logger(__name__)


class MistsHandler(object):
    def __init__(self, runner, case_gen, static_mist=None):
        self._runner = runner
        self._mists_c = None
        self._static_mist = static_mist or list()
        self._last_mist = None
        self._case_gen = case_gen

    def _test_logger(self, *args, **kwargs):
        use_doc = kwargs.get('use_doc', False)
        # FIXME: not only info
        if use_doc:
            self._runner.doc_logger.info(*args)
        else:
            self._runner.test_logger.info(*args)

    @contextlib.contextmanager
    def start_handle(self):
        self._mists_c = MistsContainer(self._static_mist)
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
        else:
            self._test_logger("Desciption: Need add doc for function %s" % func, use_doc=use_doc)

    def exception_logger(self, func, use_doc=False):
        self._test_logger("Unexpected excetion in %s: %s" % (func, traceback.format_exc()), use_doc=use_doc)

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
        tgt_env = new_env or self._runner.env
        params = self._runner.params
        test_func = doc_func if only_doc else func

        # FIXME: remove this
        if isinstance(func, StaticMist):
            return

        mist = self._check_mists(mists, self._runner.env, func, new_env)
        LOGGER.debug("Func %s mist %s", test_func, mist)
        LOGGER.debug("Env: %s", tgt_env)
        if mist:
            name, mist_obj = mist
            mist_func = mist_obj.doc_func if only_doc else mist_obj.func
            if not mist_func:
                raise Exception("Cannot find func for mist %s" % mist_obj)
            self.desc_logger(mist_func, only_doc)
            # TODO: here will raise a exception which require the caller handle this
            try:
                mist_func(name, test_func, params, tgt_env)
            except MistClearException:
                mists.remove(mist_obj)
            except MistDeadEndException:
                raise TestEndException
            except Exception as e:
                LOGGER.error('Func %s failed %s', mist_func, e)
                self.exception_logger(mist_func, only_doc)
                raise TestEndException
            # TODO: mist in the mist
            new_mist = None
        else:
            self.desc_logger(test_func, only_doc)

            if is_TestObject(test_func):
                test_func = test_func()
            try:
                new_mist = test_func(params, tgt_env)
            except ObjectFailedException:
                # TODO
                raise
            except Exception as e:
                LOGGER.error('Func %s failed %s', test_func, e)
                self.exception_logger(test_func, only_doc)
                raise TestEndException

        if new_mist and mists is not None:
            LOGGER.debug('Add a new mist %s', new_mist)
            mists.append(new_mist)
            self._last_mist = new_mist

    def _gen_mist_cases(self, mist, old_case, src_env=None, test_func=None):
        # Here we get a new mist in the test func
        # we need to trigger this mist
        if not src_env:
            src_env = self._runner.env
        history_steps = Case(list(old_case.steps),
                             tgt_env=old_case.tgt_env,
                             cleanups=old_case.cleanups)
        if test_func:
            history_steps.append(test_func)

        for name, extra_step in self._find_mist_routes(mist, src_env):
            new_case = history_steps + extra_step
            LOGGER.debug("create a new case: %s", list(new_case.steps))
            LOGGER.debug("history steps: %s, extra_step: %s",
                         list(history_steps.steps), list(extra_step.steps))
            yield name, new_case

    def _find_mist_routes(self, mist, src_env=None, with_name=True):
        routes = []
        if src_env is None:
            src_env = self._runner.env

        for name, data in mist._areas.items():
            start_env, end_env = data
            for case_obj in self._case_gen.gen_cases_special(src_env, start_env, end_env):
                if with_name:
                    yield name, case_obj
                else:
                    yield case_obj

    def gen_cases(self, test_func, need_cleanup=None):
        if isinstance(test_func, StaticMist):
            # TODO: support cleanup
            return self._find_mist_routes(test_func, with_name=False)
        else:
            # TODO: check if it is func
            return self._case_gen.gen_cases(test_func, need_cleanup=need_cleanup)

    def gen_multi_test_objects_cases(self, test_funcs, need_cleanup=None):
        return self._case_gen.gen_multi_test_objects_cases(test_funcs, need_cleanup=need_cleanup)

    def gen_cleanups(self, src_env, tgt_env):
        return self._case_gen.gen_cleanups(src_env, tgt_env)


class MistsContainer(list):
    """
    A list to store the mist
    """
