#!/usr/bin/env python

from __future__ import division
import sys

from tentapp.colors import *

NPASS = 0
NFAIL = 0

def begin(name=''):
    """Reset the pass and fail counters
    """
    global NPASS, NFAIL
    NPASS = NFAIL = 0
    if name:
        print 'beginning tests: ' + white(name)
    else:
        print 'beginning tests'

def end():
    """Print a summary of passes and fails
    """
    global NPASS, NFAIL
    print
    if NFAIL:
        print '%s tests passed'%NPASS
        print red('%s tests failed'%NFAIL)
    else:
        print green('%s tests passed'%NPASS)

def passs():
    global NPASS, NFAIL
    print green('.'),
    sys.stdout.flush()
    NPASS += 1

def fail(msg=''):
    global NPASS, NFAIL
    NFAIL += 1
    print
    print red('    fail: %s'%msg)


def eq(a,b, msg=''):
    """Expect a and b to be equal.  If not, fail.
    """
    if a == b: passs()
    else: fail(msg)

