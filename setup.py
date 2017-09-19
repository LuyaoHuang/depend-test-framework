#!/usr/bin/env python
import glob
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

import depend_test_framework


REQUIREMENTS = [
    'progressbar2',
    'PyYAML',
]

DATA_FILES = [
    ('share/depend_test_framework/examples', glob.glob('examples/*'))
]

PACKAGES = [
    'depend_test_framework',
]


class PyTest(TestCommand):
    # From https://docs.pytest.org/en/latest/goodpractices.html
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = '-x tests'

    def run_tests(self):
        import shlex
        #import here, cause outside the eggs aren't loaded
        import pytest
        print shlex.split(self.pytest_args)
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


if __name__ == '__main__':
    setup(
        name='depend_test_framework',
        version=depend_test_framework.__version__,
        url=('https://github.com/LuyaoHuang/depend-test-framework'),
        license='MIT',
        author='Luyao Huang',
        author_email='lhuang@redhat.com',
        description='A test framework which use dependency of test step to generate test case',
        scripts=glob.glob('scripts/*'),
        tests_require=['pytest'],
        packages=PACKAGES,
        data_files=DATA_FILES,
        cmdclass={'test': PyTest},
        install_requires=REQUIREMENTS,
    )
