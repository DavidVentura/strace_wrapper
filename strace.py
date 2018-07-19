#!/usr/bin/env python3
import re
import subprocess
import sys

basic_parser = re.compile(r'^(?P<command>\w+)(?P<arguments>\(.*?\"(?P<path>.*?)\".*?\)).*\((?P<desc>.*?)\)')

def trace(command):
    strace = ['strace', '--']
    strace.extend(command)
    proc = subprocess.Popen(strace, stderr=subprocess.PIPE)
    for line in proc.stderr:
        yield line

def _filter(line):
    ignored_tokens = ['.so', 'LC_MESSAGES', '/selinux', 'ioctl(', 'LC_TIME']
    _line = line.decode('ascii').rstrip()

    if '= -' not in _line:
        return False

    for ignored in ignored_tokens:
        if ignored in _line:
            return False

    return _line

def pretty(line):
    m = basic_parser.match(line)
    if not m:
        return "?? %s" % line
    return "Executing '%s' on '%s' resulted in '%s'\tFull args: %s" % (m.group('command'), m.group('path'), m.group('desc'), m.group('arguments'))

def parse_arguments():
    if len(sys.argv) < 2:
        return None

    if sys.argv[1] == '--raw':
        return {'raw': True, 'command': sys.argv[2:]}

    return {'raw': False, 'command': sys.argv[1:]}

def main(args):
    if args is None:
        print("Give me at least a command to run!")
        sys.exit(1)
    if args['raw']:
        for line in trace(args['command']):
            print(line)
    else:
        for line in trace(args['command']):
            _line = _filter(line)
            if _line:
                print(pretty(_line))


if __name__ == '__main__':
    args = parse_arguments()
    main(args)
