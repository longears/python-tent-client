#!/usr/bin/env python

from __future__ import division
import time
import random
import pprint
import string
import hashlib
import json
import requests
import webbrowser
import macauthlib
from urllib import urlencode
from colors import *



# myauthtokens should be a short file that looks like this:
#   entity = 'http://yourname.tent.is'
#   mac_key_id = 'u:asdfasdfa'
#   mac_key = 'asdfasdfasdfasdfasdfasdfasdf'

import myauthtokens



#-------------------------------------------------------------------------------------
#--- UTILS

def debugAuth(s=''): print blue('%s'%s)
def debugMain(s=''): print yellow('%s'%s)
def debugError(s=''): print red('ERROR: %s'%s)
def debugDetail(s=''): print cyan('    %s'%s)
def debugJson(s=''): print magenta(pprint.pformat(s))
def debugRequest(s=''): print green(' >> %s'%s)
def debugRaw(s=''): print white('>       '+s.replace('\n','\n>       '))

def randomString():
    return ''.join([random.choice(string.letters+string.digits) for x in xrange(20)])

# hook up sign_request() to be called on every request
def authHook(req):
    debugAuth('auth hook. mac key id: %s'%repr(myauthtokens.mac_key_id))
    debugAuth('auth hook. mac key: %s'%repr(myauthtokens.mac_key))
    macauthlib.sign_request(req, id=myauthtokens.mac_key_id, key=myauthtokens.mac_key, hashmod=hashlib.sha256)
    return req

# set up a global session using our auth hook
session = requests.session(hooks={"pre_request": authHook})


#-------------------------------------------------------------------------------------
#--- APP

class TentApp(object):
    def __init__(self,serverDiscoveryUrl):
        debugMain('init: %s'%serverDiscoveryUrl)
        self.serverDiscoveryUrl = serverDiscoveryUrl
        self.hostname = serverDiscoveryUrl.replace('https://','').split('/')[0] # HACK
        self.apiRootUrls = []
        self.discoverAPIUrls(self.serverDiscoveryUrl)

        # details of this app
        #  basic
        self.name = 'python-tent-client'
        self.description = 'description of my test app'

        #  urls
        self.url = 'http://zzzzexample.com'
        self.icon = 'http://zzzzexample.com/icon.png'
        self.oauthCallbackUrl = 'http://zzzzexample.com/oauthcallback'
        self.postNotificationUrl = 'http://zzzzexample.com/notification'

        #  permissions to request
        self.scopes = {
            'read_posts': 'x',
            'write_posts': 'x',
            'import_posts': 'x',
            'read_profile': 'x',
            'write_profile': 'x',
            'read_followers': 'x',
            'write_followers': 'x',
            'read_followings': 'x',
            'write_followings': 'x',
            'read_groups': 'x',
            'write_groups': 'x',
            'read_permissions': 'x',
            'write_permissions': 'x',
            'read_apps': 'x',
            'write_apps': 'x',
            'follow_ui': 'x',
            'read_secrets': 'x',
            'write_secrets': 'x',
        }
        self.profile_info_types = ['all']
        self.post_types = ['all']

        # auth-related things
        #  set by us
        self.state = None
        #  obtained from the server
        self.appID = None # the server assigns this to us during registration

        #  keys
        #   At first these are set to temp values during the registration & oauth approval process.
        #   When that completes, they are replaced with our permanent keys.
        self.mac_key_id = None
        self.mac_key = None
        self.mac_algorithm = None

    def discoverAPIUrls(self,serverDiscoveryUrl):
        """set self.apiRootUrls, return None
        """
        # get self.serverDiscoveryUrl doing just a HEAD request
        # look in HTTP header for Link: foo; rel="$REL_PROFILE"
        # TODO: if not, get whole page and look for <link href="foo" rel="$REL_PROFILE" />
        debugRequest('discovering: %s'%serverDiscoveryUrl)
        r = requests.head(url=serverDiscoveryUrl)

        # TODO: the requests api here only returns one link even when there are more than one in the
        # header.  I think it returns the last one, but we should be using the first one.
        self.apiRootUrls = [ r.links['https://tent.io/rels/profile']['url'] ]

        # remove trailing "/profile" from urls
        for ii in range(len(self.apiRootUrls)):
            self.apiRootUrls[ii] = self.apiRootUrls[ii].replace('/profile','')

        debugDetail('server api urls = %s'%self.apiRootUrls)

    def _register(self):
        # get self.appID and self.mac_* from server
        # return none
        debugMain('registering...')

        # describe ourself to the server
        appInfoJson = {
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'icon': 'http://example.com/icon.png',
            'redirect_uris': [self.oauthCallbackUrl],
            'scopes': self.scopes
        }
        debugJson(appInfoJson)

        headers = {
            'Content-Type': 'application/vnd.tent.v0+json',
            'Accept': 'application/vnd.tent.v0+json',
        }
        requestUrl = self.apiRootUrls[0] + '/apps'
        debugRequest('posting to %s'%requestUrl)
        r = requests.post(requestUrl, data=json.dumps(appInfoJson), headers=headers)

        # get oauth key in response
        debugDetail('headers from server:')
        debugJson(r.headers)
        debugDetail('json from server:')
        debugJson(r.json)
        if r.json is None:
            debugError('not json.  here is the actual body text:')
            debugRaw(r.text)
            return
        self.appID = r.json['id'].encode('utf-8')
        self.mac_key_id = r.json['mac_key_id'].encode('utf-8')
        self.mac_key = r.json['mac_key'].encode('utf-8')
        self.mac_algorithm = r.json['mac_algorithm'].encode('utf-8')
        debugDetail('registered successfully.  details:')
        debugDetail('  app id: %s'%repr(self.appID))
        debugDetail('  mac key: %s'%repr(self.mac_key))
        debugDetail('  mac key id: %s'%repr(self.mac_key_id))
        debugDetail('  mac algorithm: %s'%repr(self.mac_algorithm))

    def oauthRegister(self):

        # first, register with the server to set
        #  self.appID and self.mac_*
        self._register()

        debugMain('oauth')

        # send user to the tent.is url to grant access
        # we will get the "code" in response
        self.state = randomString()
        params = {
            'client_id': self.appID,
            'redirect_uri': self.oauthCallbackUrl,
            'state': self.state,
            'scope': ','.join(self.scopes.keys()),
            'tent_profile_info_types': 'all',
            'tent_post_types': 'all',
            'tent_notification_url': self.postNotificationUrl,
        }
        requestUrl = self.apiRootUrls[0] + '/oauth/authorize'
        urlWithParams = requestUrl + '?' + urlencode(params)

        print '---------------------------------------------------------\\'
        print
        print 'Opening web browser so you can grant access on tent.is.'
        print
        print 'After you grant access, your browser will be redirected to'
        print 'a nonexistant page.  Look in the url and find the "code"'
        print 'parameter.  Paste it here:'
        print
        print 'Example:'
        print 'http://zzzzexample.com/oauthcallback?code=15673b7718651a4dd53dc7defc88759e&state=ahyKV...'
        print '                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
        print
        webbrowser.open(urlWithParams)
        code = raw_input('> ')
        print
        print '---------------------------------------------------------/'

        # trade the code for a permanent key
        # first make the auth headers using the credentials from the registration step
        resource = '/apps/%s/authorizations'%self.appID
        jsonPayload = {'code':code, 'token_type':'mac'}

        # set up the tokens so they'll be picked up by the auth hook
        myauthtokens.mac_key_id = self.mac_key_id
        myauthtokens.mac_key = self.mac_key

        # then construct and send the request
        print
        headers = {
            'Content-Type': 'application/vnd.tent.v0+json',
            'Accept': 'application/vnd.tent.v0+json',
        }
        requestUrl = self.apiRootUrls[0] + resource
        debugRequest('posting to: %s'%requestUrl)
        r = session.post(requestUrl, data=json.dumps(jsonPayload), headers=headers)

        # display our request
        debugDetail('request headers:')
        debugJson(r.request.headers)
        debugDetail('request data:')
        debugDetail(r.request.data)

        # then get the response
        print
        debugDetail('response headers:')
        debugJson(r.headers)
        debugDetail('response text:')
        debugRaw(r.text)
        if not r.json:
            print
            debugError('auth failed.')
            return
        debugJson(r.json)

        # now we have permanent keys
        self.mac_key_id = r.json['access_token'].encode('utf-8')
        self.mac_key = r.json['mac_key'].encode('utf-8')
        debugDetail('final mac key id: %s'%self.mac_key_id)
        debugDetail('final mac key: %s'%self.mac_key)

        # put them where the auth hook can see them
        myauthtokens.mac_key_id = self.mac_key_id
        myauthtokens.mac_key = self.mac_key

        # TODO: we need to save the keys to disk
        #  so we can use them in future requests to get actual work done
        

    def _genericGet(self,resource):
        requestUrl = self.apiRootUrls[0] + resource
        headers = {'Accept': 'application/vnd.tent.v0+json'}
        debugRequest(requestUrl)
        r = requests.get(requestUrl,headers=headers)
        if r.json is None:
            debugError('not json.  here is the actual body text:')
            debugRaw(r.text)
            return
        return r.json


    def getProfile(self):
        # this can happen without auth
        debugMain('getProfile')
        return self._genericGet('/profile')

    def putProfile(profileType,value):
        # PUT /profile/$profileType
        pass
    
    def follow(self,entityUrl):
        # POST /followings
        pass

    def getEntitiesIFollow(self,id=None):
        # GET /followings  [/$id]
        debugMain('getEntitiesIFollow')
        return self._genericGet('/followings')

    def unfollow(self,id):
        # DELETE /followings/$id
        pass

    def getFollowers(self,id=None):
        # GET /followers  [/$id]
        debugMain('getFollowers')
        return self._genericGet('/followers')

    def removeFollower(self,id):
        # DELETE /followers/$id
        pass

    def putPost(self,post,attachments=[]):
        debugMain('putPost')

        resource = '/posts'
        requestUrl = self.apiRootUrls[0] + resource
        headers = {
            'Content-Type': 'application/vnd.tent.v0+json',
            'Accept': 'application/vnd.tent.v0+json',
        }
        debugRequest('posting to: %s'%requestUrl)
        r = session.post(requestUrl, data=json.dumps(post), headers=headers)

        debugDetail('request headers:')
        debugJson(r.request.headers)
        print
        debugDetail('request data:')
        debugRaw(r.request.data)
        print
        print yellow('  --  --  --  --  --')
        print
        debugDetail('response headers:')
        debugJson(r.headers)
        print
        debugDetail('response body:')
        debugRaw(r.text)
        print

        if r.json is None:
            debugError('failed to put post.')
            print
        return r.json

    def getPosts(self,id=None):
        # GET /posts  [/$id]
        debugMain('getPosts')
        return self._genericGet('/posts')

    def getPostAttachment(self,id,filename):
        # GET /posts/$id/attachments/$filename
        pass


#-------------------------------------------------------------------------------------
#--- MAIN

if __name__ == '__main__':
    print yellow('-----------------------------------------------------------------------\\')

    # "entity" is the Tent term for the URL to your Tent server
    # For tent.is it should be "https://yourname.tent.is"
    # Instantiating this class will perform discovery on the entity URL
    app = TentApp(myauthtokens.entity)

    # Try to get new auth credentials
    # Currently they are not saved anywhere so we have to go through the whole
    #  oauth approval flow every time
    app.oauthRegister()

    # try to post a status message using keys from myauthtokens
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

    # Read various public things that don't require auth
    profile = app.getProfile()
    debugJson(profile)
    followings = app.getEntitiesIFollow()
    debugJson(followings)
    followers = app.getFollowers()
    debugJson(followers)
    posts = app.getPosts()
    debugJson(posts)


    print yellow('-----------------------------------------------------------------------/')





