#!/usr/bin/env python

from __future__ import division
import pprint, time
import tentapp
from colors import *

def debugJson(s=''): print magenta(pprint.pformat(s))

print yellow('-----------------------------------------------------------------------\\')

# turn on debug output from tentapp
tentapp.debug = True


# "entity" is the Tent term for the URL to your Tent server.
# For tent.is it should be "https://yourname.tent.is"
# Instantiating this class will perform discovery on the entity URL
app = tentapp.TentApp('https://rabbitwhiskers.tent.is')


# Read various public things that don't require auth
profile = app.getProfile()
debugJson(profile)

followings = app.getEntitiesIFollow()
debugJson(followings)

followers = app.getFollowers()
debugJson(followers)

posts = app.getPosts()
debugJson(posts)


# Check for Oauth saved credentials. Otherwise register for new auth credentials
app.oauthRegister()


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

