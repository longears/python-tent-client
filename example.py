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
app = tentapp.TentApp('https://rabbitwhiskers.tent.is')


# Check for Oauth saved credentials. Otherwise register for new auth credentials
app.oauthRegister()


# Read various public things that don't require auth
# Note that when auth is present, these may return additional results
profile = app.getProfile()
debugJson(profile)

followings = app.getFollowings()
debugJson(followings)

followers = app.getFollowers()
debugJson(followers)


# Post a new status message
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

