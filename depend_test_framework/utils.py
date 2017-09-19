import subprocess
import sys
from contextlib import contextmanager


def run_cmd(cmd):
    return subprocess.check_output(cmd.split())


def pretty(d, indent=0):
    ret = ""
    ret += ('\t' * indent + '{\n')
    for key, value in d.iteritems():
        ret += ('\t' * indent + str(key) + ' :\n')
        if isinstance(value, dict):
            ret += pretty(value, indent + 1)
        else:
            ret += ('\t' * (indent + 1) + str(value) + ',\n')
    ret += ('\t' * indent + '}\n')
    return ret


class ProgressBar(object):
    toolbar_width = 0
    cur_step = 0

    @classmethod
    def clear(cls):
        cls.next_step(cls.toolbar_width, cls.toolbar_width)
        sys.stdout.write("\n")
        cls.toolbar_width = 0
        cls.cur_step = 0

    @classmethod
    def create_new_one(cls, prefix_name, toolbar_width):
        cls.toolbar_width = toolbar_width
        sys.stdout.write("%s [%s]" % (prefix_name, " " * toolbar_width))
        sys.stdout.flush()
        sys.stdout.write("\b" * (toolbar_width + 1))

    @classmethod
    def next_step(cls, cur, total):
        new_step = cur / float(total) * cls.toolbar_width
        delta = int(new_step) - cls.cur_step
        if delta > 0:
            sys.stdout.write("=" * delta)
            sys.stdout.flush()
            cls.cur_step += delta

    @classmethod
    @contextmanager
    def enter(cls, name, width=10):
        cls.create_new_one(name, width)
        yield
        cls.clear()
