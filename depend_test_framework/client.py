"""
Some helpers to help build client app
"""
import itertools
import sys
import os
import yaml
import copy
import importlib

from base_class import Params


def load_template(template_file):
    with open(template_file) as fp:
        data = yaml.load(fp)

    cases = data['case']
    common_params = data['params']
    for case in cases:
        params = Params(common_params)
        if 'params' in case.keys():
            params.update(case['params'])
        modules = list(load_modules(case['modules']))
        doc_modules = list(load_modules(case['doc-modules']))
        test_objs = list(load_objs(case['test_objs']))
        if 'params_matrix' in case.keys():
            for extra_params in full_permutations(case['params_matrix']):
                new_params = Params(params)
                new_params.update(extra_params)
                yield new_params, modules, doc_modules, copy.deepcopy(test_objs)
        else:
            yield params, modules, doc_modules, copy.deepcopy(test_objs)


def load_modules(modules_list, module_path='.'):
    # TODO
    cmd_folder = os.path.realpath(module_path)
    sys.path.insert(0, cmd_folder)
    for module in modules_list:
        yield importlib.import_module(module)


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
        raise Exception
