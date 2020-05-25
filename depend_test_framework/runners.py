"""
Helper classes to help run test case
"""

from .log import get_logger
from .env import Env
from .dependency import get_all_depend, Consumer
from .test_object import TestEndException, ObjectFailedException, CleanUpMethod

LOGGER = get_logger(__name__)


class Runner(object):
    def __init__(self, params, checkpoints, doc_funcs,
                 test_logger, doc_logger, env=None):
        self.params = params
        self.env = env or Env()
        # this new env only used when test object failed
        self._new_env = None
        self._checkpoints = checkpoints
        self.test_logger = test_logger
        self.doc_logger = doc_logger
        self._doc_funcs = doc_funcs
        self._extra_handler = None

    def full_logger(self, msg):
        self.test_logger.info(msg)
        self.doc_logger.info(msg)

    def set_extra_handler(self, extra_handler):
        self._extra_handler = extra_handler

    def find_checkpoints(self):
        ret = []
        for func in self._checkpoints:
            requires = get_all_depend(func, depend_cls=Consumer)
            if self.env.hit_requires(requires):
                ret.append(func)
        return ret

    def _get_doc_func(self, func):
        # FIXME: this is check for mist class
        # but this is a kind of hard coding and
        # it is also very urgly
        if getattr(func, 'doc_func', None):
            return func.doc_func

        if getattr(func, '__name__', None):
            doc_func_name = func.__name__
        else:
            doc_func_name = func.__class__.__name__

        if doc_func_name not in self._doc_funcs.keys():
            return
        return self._doc_funcs[doc_func_name]

    def run_one_step(self, func, step_index=None, check=False, only_doc=True):
        if step_index is not None:
            # TODO: move doc_logger definition in basic engine
            if only_doc:
                self.doc_logger.info('%d.\n' % step_index)
            else:
                self.full_logger('%d.\n' % step_index)
            step_index += 1

        doc_func = self._get_doc_func(func)
        if not doc_func and only_doc:
            raise Exception("Not define %s name in doc modules" % func)
        LOGGER.debug("Start transfer env, func: %s env: %s", func, self.env)
        self._new_env = new_env = self.env.gen_transfer_env(func)
        if new_env is None:
            raise Exception("Fail to gen transfer env")

        LOGGER.debug("Env transfer to %s", new_env)

        # XXX: we transfer the env before the test func, and test func can update info in the env
        if self._extra_handler:
            self._extra_handler.handle_func(func, doc_func, new_env, only_doc)
        else:
            if only_doc:
                doc_func(self.params, new_env)
            else:
                func(self.params, new_env)
        self.env = new_env

        if not check:
            return step_index

        checkpoints = self.find_checkpoints()
        for i, checkpoint in enumerate(checkpoints):
            if checkpoint == func:
                continue
            step_index = self.run_one_step(checkpoint,
                step_index=step_index, only_doc=only_doc)

        return step_index

    def _run_case_internal(self, case, case_id, test_func, need_cleanup, only_doc):
        step_index = 1
        extra_cases = {}
        self.full_logger("=" * 8 + " case %d " % case_id + "=" * 8)
        have_extra_cases = False
        try:
            steps = list(case.steps)
            LOGGER.debug("Case steps: %s", steps)
            if test_func:
                test_func = test_func
            else:
                test_func = steps[-1]
                steps = steps[:-1]

            for func in steps:
                # TODO support real case
                step_index = self.run_one_step(func,
                    step_index=step_index, only_doc=only_doc)

            with self._extra_handler.watch_func():
                step_index = self.run_one_step(test_func,
                        step_index=step_index,
                        check=self.params.extra_check,
                        only_doc=only_doc)

            tmp_cases = self._extra_handler.gen_extra_cases(case, self.env, test_func)
            if tmp_cases:
                have_extra_cases = True
                for cases_name, case in tmp_cases:
                    extra_cases.setdefault(cases_name, []).append(case)
            cleanup_steps = case.cleanups
        except TestEndException:
            cleanup_case = self._extra_handler.gen_cleanups(self.env, Env())
            if cleanup_case:
                cleanup_steps = cleanup_case.steps
            else:
                cleanup_steps = None
        except ObjectFailedException as e:
            # TODO: maybe need clean up
            LOGGER.error('Case %s failed at step %s: %s', case, step_index, e)
            if e.cleanup_method is CleanUpMethod.not_effect:
                # In this case, we don't need do anything
                pass
            else:
                # TODO
                raise NotImplementedError
        if need_cleanup:
            if not cleanup_steps:
                LOGGER.info("Cannot find clean up way")
                LOGGER.info("Current Env: %s", self.env)
            else:
                for func in cleanup_steps:
                    step_index = self.run_one_step(func, step_index=step_index, only_doc=only_doc)
        # TODO: remove this
        self.env = Env()
        return extra_cases, have_extra_cases

    def run_case(self, case, case_id, test_func=None, need_cleanup=None, only_doc=True):
        if self._extra_handler:
            with self._extra_handler.start_handle():
                return self._run_case_internal(case, case_id, test_func, need_cleanup, only_doc)
        else:
            return self._run_case_internal(case, case_id, test_func, need_cleanup, only_doc)
