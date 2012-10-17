#!/usr/bin/env python

from __future__ import division
import pprint, time
import webbrowser
import tentapp
from tentapp.colors import *

def debugJson(s=''): print magenta(pprint.pformat(s))

print yellow('-----------------------------------------------------------------------\\')


# Turn on or off the verbose debug output from tentapp
tentapp.debug = False


# "entity" is the Tent version of a username.  It's a full URL.
# For tent.is it should be "https://yourname.tent.is"
# Instantiating this class will perform discovery on the entity URL
entityUrl = 'https://pythonclienttest.tent.is'
app = tentapp.TentApp(entityUrl)


# set up the details for our app before we register it with the server
app.appDetails = {
    'name': 'python-tent-client example',
    'description': 'description of my app',
    'url': 'http://zzzzexample.com',
    'icon': 'http://zzzzexample.com/icon.png',
    'oauthCallbackURL': 'http://zzzzexample.com/oauthcallback',
    'postNotificationUrl': None,
}


#=== AUTHENTICATION BEGIN ===
# You can comment out all of this auth code if you're only
# using publicly available API methods
# You can also replace this whole block of auth code with this
# single helper method:
#     app.authorizeFromCommandLine('keystore.js')
# but this whole block of code is provided so you can see
# how auth works in more detail.

# Load auth keys from disk if they've been previously saved
keyStore = tentapp.KeyStore('keystore.js')
app.keys = keyStore.get(entityUrl, {})

# If the app has never been registered with the server, register now
if not app.hasRegistrationKeys():
    app.register()
    keyStore.save(entityUrl, app.keys)

# Ask the user to approve our app at their Tent server.
# After that, they'll be redirected to our callback URL.
# If they've already approved the app (and are logged in),
# they will be instantly redirected back to our callback URL.
if not app.hasPermanentKeys():
    approvalURL = app.getUserApprovalURL()
    print '-----------'
    print
    print 'READ THIS CAREFULLY'
    print 'Press enter to be redirected to this URL on your tent server:'
    print
    print approvalURL
    print
    print 'Your tent server will ask you to approve the app.  After that, you'
    print 'will be redirected to an apparently broken page at zzzzexample.com.'
    print 'Look in your browser\'s URL bar and find the "code" parameter.  Copy and'
    print 'paste it back into this shell.'
    print
    raw_input('    ... press enter to open browser ...')
    webbrowser.open(approvalURL)
    print
    print 'Example:'
    print 'http://zzzzexample.com/oauthcallback?code=15673b7718651a4dd53dc7defc88759e&state=ahyKV...'
    print '                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
    print 'Enter the code:'
    code = raw_input('> ')
    print '-----------'
    app.getPermanentKeys(code)
    keyStore.save(entityUrl, app.keys)

#=== AUTHENTICATION END ===


# Read various public things that don't require auth
# Note that when auth is present, these may return additional results
print yellow('PROFILE:')
profile = app.getProfile()
debugJson(profile)

print yellow('FOLLOWINGS[0]:')
followings = app.getFollowings()
debugJson(followings[0])

print yellow('FOLLOWERS[0]:')
followers = app.getFollowers()
debugJson(followers[0])

print yellow('POSTS[0]:')
posts = app.getPosts()
debugJson(posts[0])


# Post a new status message
if app.hasPermanentKeys():
    text = "This is a test message from python-tent-client's example.py.  The time is %s"%int(time.time())
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
    print yellow('A message has been posted to pythonclienttest.tent.is:')
    print cyan('    '+text)


print yellow('-----------------------------------------------------------------------/')

