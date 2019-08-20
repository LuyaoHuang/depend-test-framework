import importlib
import yaml

from copy import deepcopy
from contextlib import contextmanager


class BaseObject(object):
    def __init__(self, gen=False):
        self._gen = gen
        self._dynamic_data = None

    def parse(self, data):
        d_data = {}
        for key, value in data.items():
            obj = self._get_member(key)
            d_data[key] = obj.parse(value)
        return self.build_real_obj(d_data)

    def get_data(self):
        ret = dict()
        for name, obj in self._dynamic_data.items():
            ret[name] = obj.get_data()
        return ret

    def _get_member(self, key):
        obj = getattr(self, key)
        if not obj or not isinstance(obj, BaseObject):
            raise Exception
        return obj

    def compute(self, data, typ=None):
        with self._compute(self, data, typ=typ):
            for name, obj in self._dynamic_data.items():
                obj.compute(data, typ=typ)

    def build_real_obj(self, datas):
        new_obj = self.copy
        new_obj._dynamic_data = dict()
        for key, value in datas.items():
            new_obj._dynamic_data[key] = value
        return new_obj

    @contextmanager
    def _compute(self, data, typ=None):
        raise NotImplementedError

    @property
    def copy(self):
        return deepcopy(self)


class Option(BaseObject):
    def __init__(self, options, gen=False):
        super(Option, self).__init__(gen=gen)
        self._options = options
        self._data = None

    def parse(self, data):
        if data not in self._options:
            raise Exception
        self._data = data
        return self

    def get_data(self):
        return self._data


class Data(BaseObject):
    def __init__(self, type=None, gen=False):
        super(Data, self).__init__(gen=gen)
        self._type = type
        self._data = None

    def parse(self, data):
        if self._type and type(data) != self._type:
            raise Exception
        self._data = data
        return self

    def get_data(self):
        return self._data


class DynamicObj(BaseObject):
    def __init__(self, name, gen=False):
        super(DynamicObj, self).__init__(gen=gen)
        self._name = name
        self._real_obj = None

    def parse(self, data):
        self._import_obj()
        return self._real_obj.parse(data)

    def _import_obj(self):
        module = importlib.import_module('depend_test_framework.params_generator')
        if not module:
            raise Exception
        cls = getattr(module, self._name)
        if not cls:
            raise Exception
        # TODO: params
        self._real_obj = cls()

    def get_data(self):
        return self._real_obj.get_data()


class List(BaseObject):
    def __init__(self, member_cls, gen=False):
        super(List, self).__init__(gen=gen)
        self._member_cls = member_cls
        self._data = []

    def parse(self, data):
        d_data = []
        if type(data) is not list:
            raise Exception

        if (isinstance(self._member_cls, List) or
            isinstance(self._member_cls, Dict)):
            for item in data:
                new_obj = deepcopy(self._member_cls)
                d_data.append(new_obj.parse(item))
        else:
            for item in data:
                # TODO: pass extra param
                if isinstance(self._member_cls, DynamicObj):
                    obj = deepcopy(self._member_cls)
                else:
                    obj = self._member_cls()
                d_data.append(obj.parse(item))
        return self.build_real_obj(d_data)

    def get_data(self):
        ret = []
        for obj in self._dynamic_data:
            ret.append(obj.get_data())
        return ret

    def build_real_obj(self, datas):
        new_obj = self.copy
        new_obj._dynamic_data = list()
        for data in datas:
            new_obj._dynamic_data.append(data)
        return new_obj


class Dict(BaseObject):
    def __init__(self, member_cls, gen=False):
        super(Dict, self).__init__(gen=gen)
        self._member_cls = member_cls
        self._data = {}

    def parse(self, data):
        d_data = {}
        if type(data) is not dict:
            raise Exception

        if (isinstance(self._member_cls, List) or
            isinstance(self._member_cls, Dict)):
            for name, item in data.items():
                new_obj = deepcopy(self._member_cls)
                d_data[name] = new_obj.parse(item)
        else:
            for name, item in data.items():
                # TODO: pass extra param
                if isinstance(self._member_cls, DynamicObj):
                    obj = deepcopy(self._member_cls)
                else:
                    obj = self._member_cls()
                d_data[name] = obj.parse(item)
        return self.build_real_obj(d_data)
