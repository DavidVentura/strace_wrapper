#!/usr/bin/env python3
import re
import subprocess
import sys

basic_parser = re.compile(r'^(?P<command>\w+)(?P<arguments>\(.*?\"(?P<path>.*?)\".*?\))\s+=.*\((?P<desc>.*?)\)')
args_parser = { '{sa_family': re.compile(r'htons\((?P<port>\d+)\).*inet_addr\("(?P<ip>.*?)"\)'), # socket
                'Operation now in progress': 'Operation in progress. Likely blocked waiting for SYN-ACK '
              }

def trace(command):
    strace = ['strace', '--']
    strace.extend(command)
    proc = subprocess.Popen(strace, stderr=subprocess.PIPE, stdout=sys.stderr)
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

def parse_line(line):
    m = basic_parser.match(line)
    if not m:
        return "?? %s" % line
    args = m.group('arguments')
    for k, v in args_parser.items():
        if k in args:
            if isinstance(v, re._pattern_type):
                m_args = v.search(args)
                if m_args:
                    args = m_args.groupdict()
            elif isinstance(v, str):
                args = v
    ret = m.groupdict()
    ret['arguments'] = args
    return ret

def pretty(line):
    data = parse_line(line)
    return "Executing '{command}' on '{path}' resulted in '{desc}'\targs: {arguments}".format(**data)

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
