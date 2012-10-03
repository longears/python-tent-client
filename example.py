#!/usr/bin/env python

from __future__ import division
import pprint, time
import tentapp
from colors import *

def debugJson(s=''): print magenta(pprint.pformat(s))

print yellow('-----------------------------------------------------------------------\\')


# Turn on or off the verbose debug output from tentapp
tentapp.debug = False


# "entity" is the Tent term for the URL to your Tent server.
# For tent.is it should be "https://yourname.tent.is"
# Instantiating this class will perform discovery on the entity URL
app = tentapp.TentApp('https://pythonclienttest.tent.is')


# # These are keys for http://pythonclienttest.tent.is
# # Play nice with them.
# keys = {'appID': 'qxtrbu',
#         'mac_key': 'e3d9f4d8133e0f6391387b44b7a99e23',
#         'mac_key_id': 'u:76d9253c'}
# app.authenticate(keys)


# Read various public things that don't require auth
# Note that when auth is present, these may return additional results
profile = app.getProfile()
print yellow('PROFILE:')
debugJson(profile)

followings = app.getFollowings()
print yellow('FOLLOWINGS:')
debugJson(followings)

followers = app.getFollowers()
print yellow('FOLLOWERS:')
debugJson(followers)

posts = app.getPosts()
print yellow('posts:')
debugJson(posts)


# Post a new status message
if app.isAuthenticated():
    post = {
        'type': 'https://tent.io/types/post/status/v0.1.0',
        'published_at': int(time.time()),
        'permissions': {
            'public': True,
        },
        'licenses': ['http://creativecommons.org/licenses/by/3.0/'],
        'content': {
            'text': 'This was posted using python-tent-client.  https://github.com/longears/python-tent-client',
        }
    }
    app.putPost(post)


print yellow('-----------------------------------------------------------------------/')

