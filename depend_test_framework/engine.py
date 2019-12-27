"""
Test Engine
"""
import inspect
import random
import contextlib

from .base_class import Container, Params, get_func_params_require
from .test_object import is_TestObject, is_Action, is_CheckPoint, is_Hybrid, StaticMist
from .dependency import is_Graft, get_all_depend, Provider, Consumer, Graft
from .log import get_logger, get_file_logger, make_timing_logger
from .case_generator import DependGraphCaseGenerator
from .runner_handlers import MistsHandler
from .runners import Runner
from .learning import StepsSeqScorer
from .hook import EnvHook, CaseHook

LOGGER = get_logger(__name__)
time_log = make_timing_logger(LOGGER)


# TODO: more offical
def get_name(obj):
    if getattr(obj, '__name__', None):
        return obj.__name__
    else:
        return obj.__class__.__name__


class BaseEngine(object):
    def __init__(self, modules, doc_modules, hook_module=None):
        self.modules = modules
        self.doc_modules = doc_modules
        self.hook_module = hook_module
        self.checkpoints = Container()
        self.actions = Container()
        self.hybrids = Container()
        self.grafts = Container()
        self.env_hooks = Container()
        # TODO: not used right now
        self.case_hooks = Container()
        # TODO: not use dict
        self.doc_funcs = {}
        self.params = Params()
        # TODO: support more case generator
        self.case_gen = DependGraphCaseGenerator()

        def _handle_func(func, conatiner):
            if is_TestObject(func):
                inst_func = func()
                conatiner.add(inst_func)
            else:
                conatiner.add(func)

        for module in modules:
            # TODO: remove dup code
            for _, func in inspect.getmembers(module, is_Action):
                _handle_func(func, self.actions)
            for _, func in inspect.getmembers(module, is_CheckPoint):
                _handle_func(func, self.checkpoints)
            for _, func in inspect.getmembers(module, is_Hybrid):
                _handle_func(func, self.hybrids)

            for _, func in inspect.getmembers(module, is_Graft):
                self.grafts |= Container(get_all_depend(func, depend_cls=Graft))

        for func in self.all_funcs:
            for module in self.doc_modules:
                name = get_name(func)
                if getattr(module, name, None):
                    self.doc_funcs[name] = getattr(module, name)
                    break

        if self.hook_module:
            for _, obj in inspect.getmembers(self.hook_module,
                                             lambda x: issubclass(x, EnvHook)):
                self.env_hooks.add(obj())
            for _, obj in inspect.getmembers(self.hook_module,
                                             lambda x: issubclass(x, CaseHook)):
                self.case_hooks.add(obj())

    def run(self):
        raise NotImplementedError

    def prepare(self):
        raise NotImplementedError

    @property
    def all_funcs(self):
        return self.hybrids | self.checkpoints | self.actions

    def _cb_filter_with_param(self, func):
        param_req = get_func_params_require(func)
        if not param_req:
            return False
        if not self.params >= param_req.param_depend:
            return True
        else:
            return False

    def filter_all_func_custom(self, cb):
        self.filter_func_custom(self.actions, cb)
        self.filter_func_custom(self.checkpoints, cb)
        self.filter_func_custom(self.hybrids, cb)

    def filter_func_custom(self, container, cb):
        need_remove = Container()
        for func in container:
            if cb(func):
                LOGGER.debug('Remove func ' + str(func))
                need_remove.add(func)
        container -= need_remove


class Template(BaseEngine):
    pass


class StaticTemplate(Template):
    pass


class MatrixTemplate(Template):
    pass


class Fuzz(BaseEngine):
    pass


class AI(BaseEngine):
    pass


class Demo(BaseEngine):
    """
    Standerd Engine + Mist handler + Hook support
    """
    def __init__(self, basic_modules, test_modules=None,
                 test_funcs=None, doc_modules=None, hook_module=None):
        self.test_modules = test_modules
        self.test_funcs = test_funcs
        tmp_modules = []
        tmp_modules.extend(basic_modules)
        if self.test_modules:
            tmp_modules.extend(test_modules)
        super(Demo, self).__init__(tmp_modules, doc_modules, hook_module)
        # load static mist for mist handler
        self.static_mists = Container()

        for module in tmp_modules:
            for _, cls in inspect.getmembers(module, StaticMist.issubclass):
                self.static_mists.add(cls())

    def _prepare_test_funcs(self):
        if not self.test_modules and not self.test_funcs:
            raise Exception('Need give a test object !')
        if self.test_modules:
            test_funcs = []
            for module in self.test_modules:
                for _, func in inspect.getmembers(module, (is_Action, is_Hybrid)):
                    test_funcs.append(func)
        else:
            test_funcs = self.test_funcs
        return test_funcs

    @staticmethod
    def _get_func_name(test_func):
        if getattr(test_func, 'func_name', None):
            return getattr(test_func, 'func_name')
        else:
            return str(test_func)

    def _load_extra_handler(self, runner):
        extra_handler = MistsHandler(runner, self.case_gen, static_mist=self.static_mists)
        runner.set_extra_handler(extra_handler)
        return extra_handler

    def _training(self, case_matrix, test_func):
        datas = self._create_training_data(case_matrix, test_func)
        lrn_program = StepsSeqScorer(5, func_map={func: i for i, func in enumerate(sorted(self.all_funcs))})
        lrn_program.train_and_test(list(datas))
        # lrn_program.test(list(datas))

    def _start_test(self, test_func, need_cleanup=False,
                    full_matrix=True, max_cases=None, only_doc=True):
        title = self._get_func_name(test_func)

        self.params.doc_logger = self.params.case_logger
        self.params.logger.info("=" * 8 + " %s " % title + "=" * 8)
        self.params.logger.info("")
        case_index = 1

        # create runner
        runner = Runner(self.params, self.checkpoints, self.doc_funcs,
                        self.params.logger, self.params.doc_logger)
        extra_handler = self._load_extra_handler(runner)

        # generate test case
        with time_log('Compute case permutations'):
            # TODO: is that a good idea to use handler to gen case ?
            case_matrix = sorted(list(extra_handler.gen_cases(test_func, need_cleanup=need_cleanup)))

        LOGGER.info('Find %d valid cases', len(case_matrix))

        # training part
        # self._training(case_matrix, test_func)
        # return

        # TODO use a class to be a cases container
        extra_cases = {}
        while case_matrix:
            case = case_matrix.pop(0)
            new_extra_cases, is_mist = runner.run_case(case, case_index, test_func,
                                                       need_cleanup, only_doc=only_doc)
            if not full_matrix and not is_mist:
                break
            for mist_name, cases in new_extra_cases.items():
                extra_cases.setdefault(mist_name, []).extend(cases)
            case_index += 1
            if max_cases and case_index > max_cases:
                break

        LOGGER.info("find another %d extra cases", len(extra_cases))
        self.params.doc_logger = self.params.mist_logger
        runner.doc_logger = self.params.mist_logger
        for name, extra_case in extra_cases.items():
            for case in sorted(extra_case):
                ret, is_mist = runner.run_case(case, case_index,
                                               need_cleanup=need_cleanup,
                                               only_doc=only_doc)
                if is_mist:
                    raise NotImplementedError
                case_index += 1
                if not full_matrix:
                    break

    def _create_training_data(self, cases, test_func):
        # TODO: Only for testing
        def score_a(case):
            if case.step_num >= 13:
                score = 1
            elif 10 <= case.step_num < 13:
                score = 2
            elif 9 <= case.step_num < 10:
                score = 3
            elif 7 <= case.step_num < 9:
                score = 4
            elif case.step_num < 7:
                score = 5
            return score

        def score_b(case, funcs):
            return len(set(case.steps) & set(funcs))

        random_funcs = random.sample(self.actions, 5)
        for case in cases:
            score = score_a(case)
            # score = score_b(case, random_funcs)
            steps_seq = list(case.steps)
            steps_seq.append(test_func)
            yield steps_seq, score

    @contextlib.contextmanager
    def preprare_logger(self, doc_file):
        doc_path = 'doc.file' if not doc_file else doc_file
        run_log_path = doc_path + ".log"
        self.params.logger = get_file_logger(run_log_path, run_log_path)
        if self.params.mist_rules in ('both', None):
            logger = get_file_logger(doc_path, doc_path)
            self.params.case_logger = logger
            self.params.mist_logger = logger
            yield
            LOGGER.info('Write all case to %s', doc_path)
        elif self.params.mist_rules == 'split':
            mist_file = doc_path + '-mist'
            case_file = doc_path + '-case'
            self.params.mist_logger = get_file_logger(mist_file, mist_file)
            self.params.case_logger = get_file_logger(case_file, case_file)
            yield
            LOGGER.info('Write standerd case to %s', case_file)
            LOGGER.info('Write extra case to %s', mist_file)
        else:
            raise NotImplementedError
        LOGGER.info('Write case runtime log to %s', run_log_path)

    def prepare(self):
        self.filter_all_func_custom(self._cb_filter_with_param)
        with time_log('Gen the depend map'):
            self.case_gen.gen_depend_map(self.actions | self.hybrids, self.params.drop_env)

    def run(self, params, doc_file=None):
        self.params = params
        LOGGER.debug(self.params.pretty_display())
        # TODO
        with self.preprare_logger(doc_file):
            self.prepare()

            tests = []
            test_funcs = self._prepare_test_funcs()
            self.env_hooks.imap("setup", params)

            while test_funcs:
                # TODO
                test_func = random.choice(test_funcs)
                test_funcs.remove(test_func)
                # FIXME: remove this
                if StaticMist.issubclass(test_func):
                    test_func = test_func()

                try:
                    self._start_test(test_func,
                                     full_matrix=self.params.full_matrix,
                                     max_cases=self.params.max_cases,
                                     only_doc=True if self.params.test_case else False,
                                     need_cleanup=True if self.params.cleanup else False)
                    LOGGER.info("Test %s          \033[92mPASS\033[0m\n",
                                self._get_func_name(test_func))
                except:
                    LOGGER.info("Test %s          \033[91mFAIL\033[0m\n",
                                self._get_func_name(test_func))
                    raise
                finally:
                    self.env_hooks.imap("clean_up", params)
