#!/usr/bin/env python
import glob
import sys
import os

from setuptools import setup, Command, find_packages
from setuptools.command.test import test as TestCommand

import depend_test_framework


REQUIREMENTS = [
    'progressbar2',
    'PyYAML',
    'numpy',
    'tensorflow',
]

CHECK_FILES = [
    'scripts/deptest',
    'depend_test_framework',
    'tests',
]


class PyTest(TestCommand):
    # From https://docs.pytest.org/en/latest/goodpractices.html
    user_options = [('pytest-extra-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = '-x tests'
        self.pytest_extra_args = ''

    def run_tests(self):
        import shlex
        #import here, cause outside the eggs aren't loaded
        import pytest
        args = self.pytest_args + self.pytest_extra_args
        errno = pytest.main(shlex.split(args))
        sys.exit(errno)


class SyntaxCheck(Command):
    user_options = [('pep8-extra-args=', None, "Arguments to pass to pep8"),
                    ('pylint-extra-args=', None, "Arguments to pass to pylint")]
    description = "Check code syntax using pylint and pep8"

    def initialize_options(self):
        self.pep8_extra_args = ''
        self.pylint_extra_args = ''

    def finalize_options(self):
        pass

    def run(self):
        output_format = sys.stdout.isatty() and "colorized" or "text"

        print("running pep8")
        cmd = "pep8 "
        cmd += "--config tests/pep8.cfg "
        cmd += " ".join(CHECK_FILES)
        cmd += " %s" % self.pep8_extra_args
        r = os.system(cmd)
        if r != 0:
            sys.exit(r)

        print("running pylint")
        cmd = "pylint "
        cmd += "--rcfile tests/pylint.cfg "
        cmd += "--output-format=%s " % output_format
        cmd += " ".join(CHECK_FILES)
        cmd += " %s" % self.pylint_extra_args
        r = os.system(cmd)
        if r != 0:
            sys.exit(r)


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
        packages=find_packages(exclude=['tests', 'examples']),
        cmdclass={'test': PyTest, 'syntax_check': SyntaxCheck},
        install_requires=REQUIREMENTS,
    )
