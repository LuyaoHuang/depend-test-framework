import os

from depend_test_framework.test_object import Action, CheckPoint, TestObject, ObjectFailedException, CleanUpMethod
from depend_test_framework.dependency import Provider, Consumer
from depend_test_framework.base_class import ParamsRequire


@Action.decorator(1)
@ParamsRequire.decorator(['file_path'])
@Provider.decorator('hello_world_file', Provider.SET)
def echo_hello_world_file(params, env):
    """ Use echo create a file include hello world
    """
    os.system('echo "Hello World!" > %s' % params.file_path)


@Action.decorator(1)
@ParamsRequire.decorator(['file_path'])
@Provider.decorator('hello_world_file', Provider.SET)
def write_hello_world_file(params, env):
    """ Use open() create a file include hello world
    """
    with open(params.file_path, 'w+') as fp:
        fp.write('Hello World!')


@CheckPoint.decorator(1)
@ParamsRequire.decorator(['file_path'])
@Consumer.decorator('hello_world_file', Consumer.REQUIRE)
def check_hello_world_file(params, env):
    """ Check hello world file text
    """
    with open(params.file_path, 'r') as fp:
        data = fp.read()

    params.logger.info("File %s include:\n%s", params.file_path, data)
    if data != 'Hello World!':
        params.logger.info("Result not expected: %s != Hello World!", data)
        raise ObjectFailedException(CleanUpMethod.not_effect)


@Action.decorator(1)
@ParamsRequire.decorator(['file_path'])
@Provider.decorator('hello_world_file', Provider.CLEAR)
def remove_hello_world_file(params, env):
    """ remove hello world file
    """
    os.remove(params.file_path)
