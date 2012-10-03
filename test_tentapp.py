#!/usr/bin/env python

from __future__ import division
import pprint, time
from colors import *
import testlib

import tentapp
tentapp.debug = False


print yellow('-----------------------------------------------------------------------\\')
testlib.begin('TentApp')


#-------------------------------------------------------------------------------------------
#--- AUTHENTICATION

# These are keys for http://pythonclienttest.tent.is
# Play nice with them.
keys = {
    "appID": "as3yqy", 
    "mac_key": "2dc5df2a3b3f556518aca78a79fd82cf", 
    "mac_key_id": "u:6b5fb706"
}

app = tentapp.TentApp('https://pythonclienttest.tent.is')
testlib.eq(    app.isAuthenticated(), False, 'when starting, should not be authenticated'   )

# We use the result of getFollowers to see if we're actually authenticated or not
# The resulting JSON objects will have a "groups" field if and only if the authentication is working.
aFollower = app.getFollowers()[0]
testlib.eq(    'groups' in aFollower, False, 'non-authenticated GET /followers should not have "groups"'   )

keys2 = app.authenticate(keys)
testlib.eq(    keys == keys2, True, 'authenticate(keys) should not modify the keys'   )
testlib.eq(    app.isAuthenticated(), True, 'authenticate() should affect isAuthenticated()'   )

aFollower = app.getFollowers()[0]
testlib.eq(    'groups' in aFollower, True, 'authenticated GET /followers should have "groups"'   )


#-------------------------------------------------------------------------------------------
#--- BASIC NON-AUTHENTICATED FUNCTIONALITY

app = tentapp.TentApp('https://tent.tent.is')
testlib.eq(   app.apiRootUrls, ['https://tent.tent.is/tent'], 'discovery should get the correct api root urls'   )
testlib.eq(app.isAuthenticated(), False, 'when starting, should not be authenticated')

profile = app.getProfile()
testlib.eq(   type(profile), dict, 'profile should be a dict'   )
testlib.eq(   'https://tent.io/types/info/core/v0.1.0' in profile, True, 'profile should have a "core" section'   )

followings = app.getFollowings(limit=7)
testlib.eq(   type(followings), list, 'followings should be a list'   )
testlib.eq(   type(followings[0]), dict, 'followings should be a list of dicts'   )
testlib.eq(   len(followings) == 7, True, 'getFollowings: limit parameter should work'   )

followers = app.getFollowers(limit=7)
testlib.eq(   type(followers), list, 'followers should be a list'   )
testlib.eq(   type(followers[0]), dict, 'followers should be a list of dicts'   )
testlib.eq(   len(followers) == 7, True, 'getFollowers: limit parameter should work'   )

posts = app.getPosts(limit=7)
testlib.eq(   type(posts), list, 'posts should be a list'   )
testlib.eq(   type(posts[0]), dict, 'posts should be a list of dicts'   )
testlib.eq(   len(posts) == 7, True, 'getPosts: limit parameter should work'   )


#-------------------------------------------------------------------------------------------
#--- UNICODE

# This post has a unicode snowman in it: https://longears.tent.is/posts/hkl5ci
longearsApp = tentapp.TentApp('https://longears.tent.is')
post = longearsApp.getPosts(id='hkl5ci')
testlib.eq(   u'\u2603' in post['content']['text'], True, 'unicode snowman should be present in this post'   )


testlib.end()
print yellow('-----------------------------------------------------------------------/')


