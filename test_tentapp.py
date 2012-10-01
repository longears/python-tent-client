#!/usr/bin/env python

from __future__ import division
import pprint, time
from colors import *
import testlib

import tentapp
tentapp.debug = False


print yellow('-----------------------------------------------------------------------\\')
testlib.begin('TentApp')

app = tentapp.TentApp('https://tent.tent.is')

testlib.eq(app.isAuthenticated(), False, 'when starting with no config file, should not be authenticated')

profile = app.getProfile()
testlib.eq(type(profile), dict, 'profile should be a dict')
testlib.eq('https://tent.io/types/info/core/v0.1.0' in profile, True, 'profile should have a "core" section')


testlib.end()
print yellow('-----------------------------------------------------------------------/')


