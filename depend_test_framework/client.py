"""
Some helpers to help build client app
"""
import itertools
import sys
import os
import yaml
import copy
import random
import importlib

from .base_class import Params


def _check_param(param, name, typ=None):
    if not param:
        raise KeyError("Need specify param %s" % name)

    if typ and type(param) != typ:
        raise TypeError("param %s type is not right, should be %s" % (name, typ))


def _get_and_check(data, name, typ=None):
    sub_data = data.get(name)
    _check_param(sub_data, name, typ)
    return sub_data


def load_template(template_file):
    """ Help to load a yaml template file which format like this:

        params: // required, this means global params
            test_case: True
            full_matrix: True
            guest_name: 'vm1'
            guest_xml: 'guest.xml'
            mist_rules: 'split'
            max_cases: 30
            drop_env: 3
        
        case: // required, this part for test case generate
             - name: test cases name
               params: // optional, will override global params
                 restart_libvirtd: True
                 curmem: 1048576
                 mem_period: 2
               params_matrix: // optional, will generate a matrix for each element in list
                 memballoon:
                   model:
                     - 'none'
                     - 'virtio'
               random_params:
                 curmem:
                   1048576: 0.2
                   524288: 0.8
               test_objs: // required, the target want test
                 - mem_test.virsh_set_period
               modules: // required, will help to generate case
                 - vm_basic
                 - mem_test
               doc-modules: // required, will help to generate case docuement
                 - vm_basic_doc
                 - mem_test_doc

        And this function will return generater of params, modules, doc_modules, test_objs for each case
    """
    with open(template_file) as fp:
        data = yaml.safe_load(fp)

    # TODO: create a subclass of dict to make this check to be a method
    cases = _get_and_check(data, 'case', list)
    common_params = _get_and_check(data, 'params', dict)

    for case in cases:
        params = Params(common_params)
        if 'params' in case.keys():
            params.update(case['params'])
        modules = list(load_modules(_get_and_check(case, 'modules')))
        if 'doc-modules' in case.keys():
            doc_modules = list(load_modules(_get_and_check(case, 'doc-modules')))
        else:
            doc_modules = []
        test_objs = list(load_objs(_get_and_check(case, 'test_objs')))
        if 'random_params' in case.keys():
            for param_name, tmp_data in case['random_params'].items():
                for value, rate in tmp_data.items():
                    if random.random() < float(rate):
                        break
                params[param_name] = value
        if 'params_matrix' in case.keys():
            for extra_params in full_permutations(case['params_matrix']):
                new_params = Params(params)
                new_params.update(extra_params)
                modules = reload_modules(modules)
                doc_modules = reload_modules(doc_modules)
                yield new_params, modules, doc_modules, copy.deepcopy(test_objs)
        else:
            modules = reload_modules(modules)
            doc_modules = reload_modules(doc_modules)
            yield params, modules, doc_modules, copy.deepcopy(test_objs)


def load_modules(modules_list, module_path='.'):
    # TODO
    cmd_folder = os.path.realpath(module_path)
    sys.path.insert(0, cmd_folder)
    for module in modules_list:
        yield importlib.import_module(module)


def reload_modules(modules_list):
    ret = list()
    for module in modules_list:
        ret.append(importlib.reload(module))
    return ret


def load_objs(test_objs_list):
    # TODO: only support 2 layer
    for test_obj in test_objs_list:
        tmp_module = importlib.import_module(test_obj.split('.')[0])
        yield getattr(tmp_module, test_obj.split('.')[1], None)


def full_permutations(params_matrix):
    if isinstance(params_matrix, dict):
        val_pt = []
        keys = params_matrix.keys()
        for key in keys:
            ret = full_permutations(params_matrix[key])
            if isinstance(ret, list):
                val_pt.append(ret)
            else:
                val_pt.append([ret])
        pmt = itertools.product(*val_pt)
        return [Params(zip(keys, i)) for i in pmt]
    elif isinstance(params_matrix, list):
        ret = []
        for data in params_matrix:
            tmp = full_permutations(data)
            if isinstance(tmp, list):
                ret.extend(tmp)
            else:
                ret.append(tmp)
        return ret
    elif isinstance(params_matrix, (str, int, float)):
        return params_matrix
    else:
        raise TypeError("Not support type %s" % type(params_matrix))


class ParamDoc(object):
    """ Help to generate params document
    """
    _objs = dict()

    @classmethod
    def append(cls, name, type, doc):
        cls._objs[name] = (name, cls.trans_type(type), doc)

    @staticmethod
    def trans_type(type):
        type_map = {list: "List",
                    str: "String",
                    bool: "Bool",
                    int: "Integer"}
        return type_map[type]

    @classmethod
    def gen_document(cls):
        ret = ""
        for param_data in cls._objs.values():
            ret += "%s:  %s. %s\n" % param_data
        return ret

    @classmethod
    def collect_param_doc(cls):
        pass

    @classmethod
    def dump_to_yaml(cls):
        pass


ParamDoc.append("extra_check", bool, "Set true to enable run posible checkpoints after every actions")
ParamDoc.append("mist_rules", str, "support (“both”, “split”), both:write mist case and standard case"
                " to one file. split:  split mist cases to another file named like XXX-mist")
ParamDoc.append("test_case", bool, "Set true to generate test cases and write them to case files "
                "instead of executing test cases. Set false to generate test cases and execute them.")
ParamDoc.append("max_cases", int, "Define max cases number when generate cases")
ParamDoc.append("drop_env", int, "If an env length is higher than this value, this tool will skip this env")
ParamDoc.append("test_objs", list, "A list of test action or checkpoint name which you want to test")
ParamDoc.append("modules", list, "A list of python file names which includes actions and checkpoints")
ParamDoc.append("doc-modules", list, "A list of python file names which includes actions and checkpoints. "
                "This is for manual cases generation, the each action and checkpoint name"
                "should be the same with the test execution action and checkpoint.")
ParamDoc.append("cleanup", bool, "Whether to clean up env after each test case finishes")
ParamDoc.append("suit_env_limit", int, "Increase this number if you want to generate more test cases")
ParamDoc.append("allow_dep", int, "Increase this number if you want to generate more test cases")
ParamDoc.append("min_test_level", int, "Ignore actions/checkpoints which test_level smaller than this value."
                "Test level 1-10 for actions/checkpoints which are basic operations and recommended to combine with other features."
                "Test level > 10 for actions/checkpoints which are complex or advanced operations and not recommended to combine "
                "with other features if the user is not familiar with them.")
ParamDoc.append("max_test_level", int, "Ignore actions/checkpoints which test_level bigger than this value."
                "Test level 1-10 for actions/checkpoints which are basic operations and recommended to combine with other features."
                "Test level > 10 for actions/checkpoints which are complex or advanced operations and not recommended to combine "
                "with other features if the user is not familiar with them.")
