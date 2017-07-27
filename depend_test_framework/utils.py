import subprocess

def run_cmd(cmd):
    return subprocess.check_output(cmd.split())

def pretty(d, indent=0):
    ret = ""
    ret += ('\t' * indent + '{\n')
    for key, value in d.iteritems():
        ret += ('\t' * indent + str(key) + ' :\n')
        if isinstance(value, dict):
            ret += pretty(value, indent+1)
        else:
            ret += ('\t' * (indent+1) + str(value) + ',\n')
    ret += ('\t' * indent + '}\n')
    return ret
