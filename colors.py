#!/usr/bin/env python
#
# A utility to print colored text to the shell.
# Probably doesn't work on Windows.

COLORS = {'red':'31',
          'green': '32',
          'yellow': '33',
          'blue': '34',
          'magenta': '35',
          'cyan': '36',
          'white': '37',
          'reset': '39'}
def colorText(s,color):
    # color should be a string from COLORS
    return '\033[%sm%s\033[%sm'%(COLORS[color],s,COLORS['reset'])
def red(s):     return colorText(s,'red')
def green(s):   return colorText(s,'green')
def yellow(s):  return colorText(s,'yellow')
def blue(s):    return colorText(s,'blue')
def magenta(s): return colorText(s,'magenta')
def cyan(s):    return colorText(s,'cyan')
def white(s):   return colorText(s,'white')

