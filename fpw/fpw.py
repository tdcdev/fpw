# fpw - fpw.py

# Created by Thomas Da Costa <tdc.input@gmail.com>

# Copyright (C) 2014 Thomas Da Costa

# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.

# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:

# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.


import os
import sys
import argparse
import logging
import time
import signal
import subprocess


g_process = None
g_stop = False


def signal_handler(signal, frame):
        global g_stop
        g_stop = True


def tail(logfile):
    global g_stop, g_process
    while not g_stop and g_process.poll() == None:
        try:
            with open(logfile) as f:
                while not g_stop and g_process.poll() == None:
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    yield line
        except Exception as e:
            time.sleep(0.1)


def setup(logfile, cfgfile):
    try:
        if os.path.exists(logfile):
            logging.info('Clear %s' % logfile)
            os.remove(logfile)
    except Exception as e:
        logging.error(e)
    try:
        logging.info('Create %s' % cfgfile)
        with open(cfgfile, 'w') as f:
            f.write('ErrorReportingEnable=1 TraceOutputFileEnable=1\n')
    except Exception as e:
        logging.error(e)


def get_args():
    parser = argparse.ArgumentParser(
            description = 'Run Flash Player 11 debug (SA) and display logs'
            )
    flashplayer = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            'flashplayerdebugger'
            )
    logfile = os.path.expanduser('~/.macromedia/Flash_Player/Logs/flashlog.txt')
    parser.add_argument(
            'file',
            type = str,
            nargs = '?',
            default = None,
            help = 'SWF file to run'
            )
    parser.add_argument(
            '--flashplayer',
            type = str,
            default = flashplayer,
            help = 'Flash Player executable path'
            )
    parser.add_argument(
            '--logfile',
            type = str,
            default = logfile,
            help = 'Flash Player logfile path'
            )
    parser.add_argument(
            '-v',
            '--verbose',
            action = 'store_true',
            help = 'increase output verbosity'
            )
    return parser.parse_args()


def main(args):
    global g_process
    executable = [args.flashplayer]
    if args.file:
        executable.append(args.file)
    signal.signal(signal.SIGINT, signal_handler)
    cfgfile = os.path.expanduser('~/mm.cfg')
    setup(args.logfile, cfgfile)
    logging.info('Launch process %s' % executable)
    g_process = subprocess.Popen(executable)
    for line in tail(args.logfile):
        sys.stdout.write('> %s' % line)
    if g_process.poll() == None:
        logging.info('Kill process %s' % executable)
        g_process.terminate()
    try:
        if os.path.exists(cfgfile):
            logging.info('Remove %s' % cfgfile)
            os.remove(cfgfile)
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    args = get_args()
    level = logging.WARNING
    if args.verbose:
        level = logging.INFO
    logging.basicConfig(
            level = level,
            format = '%(levelname)s: %(message)s'
            )
    main(get_args())
