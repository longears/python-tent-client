#!/usr/bin/env python

from __future__ import division
import pprint, time, sys, json
from colors import *
import testlib

import tentapp
tentapp.debug = False

print yellow('-----------------------------------------------------------------------\\')
testlib.begin('TentApp')


#-------------------------------------------------------------------------------------------
#--- DISCOVERY REDIRECT VIA 3RD PARTY SITE <link> TAGS

originalEntityUrl = 'http://longearstestaccount.tumblr.com/'
tentIsEntityUrl = 'https://longearstestaccount.tent.is'
expectedRootUrls = ['https://longearstestaccount.tent.is/tent']
app = tentapp.TentApp(originalEntityUrl)
testlib.eq(   app.entityUrl, tentIsEntityUrl, '3rd party redirect via <link> tags should get correct entityUrl'   )
testlib.eq(   app.apiRootUrls, expectedRootUrls, '3rd party redirect via <link> tags should get correct apiRootUrls'   )


#-------------------------------------------------------------------------------------------
#--- AUTHENTICATION

entityUrl = 'https://pythonclienttest.tent.is'
app = tentapp.TentApp(entityUrl)

testlib.eq(    app.isAuthenticated(), False, 'when starting, should not be authenticated'   )

# We use the result of getFollowers to see if we're actually authenticated or not
# The resulting JSON objects will have a "groups" field if and only if the authentication is working.
aFollower = app.getFollowers()[0]
testlib.eq(    'groups' in aFollower, False, 'non-authenticated GET /followers should not have "groups"'   )

# Generators with no authentication
testlib.eq(   len(list(app.generateFollowers())) >= 1, True, 'generateFollowers should return at least one item'   )
testlib.eq(   len(list(app.generateFollowings())) >= 1, True, 'generateFollowings should return at least one item'   )
testlib.eq(   len(list(app.generatePosts())) >= 1, True, 'generatePosts should return at least one item'   )

# Authenticate
# You can use your own database here instead of KeyStore if you want.
# KeyStore just saves the keys to a local JSON file.
keyStore = tentapp.KeyStore('keystore.js')
if keyStore.getKey(entityUrl):
    # Reuse auth keys from a previous run
    app.authenticate(keyStore.getKey(entityUrl))
else:
    # Get auth keys for the first time
    # and save them into the keyStore
    keyStore.addKey(entityUrl, app.authenticate())

testlib.eq(    app.isAuthenticated(), True, 'authenticate() should affect isAuthenticated()'   )

aFollower = app.getFollowers()[0]
testlib.eq(    'groups' in aFollower, True, 'authenticated GET /followers should have "groups"'   )

# Generators with authentication
testlib.eq(   len(list(app.generateFollowers())) >= 1, True, 'generateFollowers should return at least one item'   )
testlib.eq(   len(list(app.generateFollowings())) >= 1, True, 'generateFollowings should return at least one item'   )
testlib.eq(   len(list(app.generatePosts())) >= 1, True, 'generatePosts should return at least one item'   )

# # A test case for the tend bug which causes the before_id param to be ignored 
# # if there are other params like post_types or entity, which results in the
# # same items being generated forever
# print
# for post in app.generatePosts(post_types='https://tent.io/types/post/status/v0.1.0'):
# # for post in app.generatePosts(entity='https://tent.tent.is'):
#     timestamp = time.asctime(time.localtime(  post['published_at']  ))
#     print cyan('%s  %s %s'%(post['id'],timestamp,post['entity']))


# post a status and then get it back
text = "This is a test message from python-tent-client's test_tentapp.py.  The time is %s"%int(time.time())
post = {
    'type': 'https://tent.io/types/post/status/v0.1.0',
    'published_at': int(time.time()),
    'permissions': {
        'public': True,
    },
    'licenses': ['http://creativecommons.org/licenses/by/3.0/'],
    'content': {
        'text': text,
    }
}
app.putPost(post)

posts = app.getPosts()
success = False
for post in posts:
    if '/status/' in post['type']:
        if post['content']['text'] == text:
            success = True
testlib.eq(   success, True, 'should be able to post a status and then get it back'   )


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


