import yaml

from .base import Dict, List, Data, Option, DynamicObj, BaseObject


class ParamsGenerator(object):
    def __init__(self):
        pass

    @classmethod
    def parse_yaml(cls, yaml_file):
        with open(yaml_file) as fp:
            data = yaml.load(fp)

        if type(data) is list:
            roots = []
            for sub_data in data:
                root = ParamsRoot()
                roots.append(root.parse(sub_data))
            return roots
        else:
            root = ParamsRoot()
            return root.parse(data)

    def generate(self):
        pass


class Param(BaseObject):
    values = List(Data)
    children = Dict(DynamicObj('Param'))


class Dependency(BaseObject):
    name = Data(type=str)
    type = Option(['conflict'])
    group = List(Dict(DynamicObj('Param')))


class Preference(BaseObject):
    name = Data(type=str)
    rate = Data(type=int)
    group = List(Dict(Param))


class ParamsRoot(BaseObject):
    name = Data(type=str)
    type = Option(['default', 'full', 'random'])
    params = Dict(Param)
    dependency = List(Dependency)
    preference = List(Preference)
