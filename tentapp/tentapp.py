#!/usr/bin/env python

from __future__ import division
import time
import random
import os
import pprint
import string
import hashlib
import hmac
from base64 import b64encode
import json
import requests
from urllib import urlencode, quote
from urlparse import urlparse
from colors import *

requests.defaults.defaults['danger_mode'] = True


class DiscoveryFailure(Exception): pass
class RegistrationFailure(Exception): pass
class AuthRequestFailure(Exception): pass
class ConnectionFailure(Exception): pass


#-------------------------------------------------------------------------------------
#--- UTILS

# Set this to True to get a ton of debugging info printed to the screen
debug = False
retries = 10

def debugAuth(s=''):
    if debug: print blue('%s'%s)
def debugMain(s=''):
    if debug: print yellow('%s'%s)
def debugError(s=''):
    if debug: print red('ERROR: %s'%s)
def debugDetail(s=''):
    if debug: print cyan('    %s'%s)
def debugJson(s=''):
    if debug: print magenta(pprint.pformat(s))
def debugRequest(s=''):
    if debug: print green(' >> %s'%s)
def debugRaw(s=''):
    if debug: print white('>       '+s.replace('\n','\n>       '))

def randomString():
    return ''.join([random.choice(string.letters+string.digits) for x in xrange(20)])

def removeUnicode(s):
    if type(s) == unicode:
        return s.encode('utf8')
    return s

def buildHmacSha256AuthHeader(mac_key_id,mac_key,method,resource,hostname,port):
    """Return an authentication header as per 
    http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-01
    """
    debugMain('HMAC SHA 256')
    debugDetail('mac key id: %s'%repr(mac_key_id))
    debugDetail('mac key: %s'%repr(mac_key))

    timestamp = int(time.time())
    nonce = randomString()

    msg = '\n'.join([str(timestamp), nonce, method, resource, hostname, str(port), '', ''])
    debugDetail('input to hash: '+repr(msg))
    debugRaw(msg)
   
    digest = hmac.new(removeUnicode(mac_key),removeUnicode(msg),hashlib.sha256).digest()
    mac = removeUnicode(b64encode(digest).decode()) # this produces unicode for some reason
    authHeader = 'MAC id="%s" ts="%s" nonce="%s" mac="%s"'%(removeUnicode(mac_key_id), timestamp, nonce, mac)
    debugDetail('auth header:')
    debugRaw(authHeader)
    return authHeader

def retry(method,*args,**kwargs):
    for ii in range(retries):
        try:
            return method(*args,**kwargs)
        except requests.exceptions.HTTPError:
            debugError('http error.  retrying... (that was attempt %s of %s)'%(ii,retries))
        except requests.exceptions.ConnectionError:
            debugError('connection error.  retrying... (that was attempt %s of %s)'%(ii,retries))
        time.sleep(1)
    print 'tried too many times'
    raise ConnectionFailure

#-------------------------------------------------------------------------------------
#--- CONSTANTS

DEFAULT_HEADERS = {
    'Accept': 'application/vnd.tent.v0+json',
}

#-------------------------------------------------------------------------------------
#--- KEYSTORE

class KeyStore(object):
    def __init__(self,filename):
        self.filename = filename
        if os.path.exists(self.filename):
            self.keys = self._load()
        else:
            self.keys = {} # mapping from entityUrl to key dictionaries

    def save(self,entityUrl,keys):
        self.keys[entityUrl] = keys
        self._save()

    def get(self,entityUrl,ifNotFound=None):
        result = self.keys.get(entityUrl,None)
        if result is None: return ifNotFound
        resultNoUnicode = {}
        for k,v in result.items():
            resultNoUnicode[removeUnicode(k)] = removeUnicode(v)
        return resultNoUnicode

    def _save(self):
        open(self.filename,'w').write(   json.dumps(self.keys, sort_keys=True, indent=4)+'\n'   )
    def _load(self):
        return json.loads(   open(self.filename,'r').read()   )

#-------------------------------------------------------------------------------------
#--- APP

class TentApp(object):
    def __init__(self,entityUrl):
        """The first time you call this you must set entityUrl.
        After that you can omit it and it will be read from the auth config file.
        If entityUrl is None and there is no auth config file, an error will be raised.
        Upon instantiation a TentApp object will perform server discovery on the entityUrl,
         so you should expect a short delay during instantiation.
        Note that the discover process can result in a new value of entityUrl under some
         circumstances(*), so your code may want to grab the new value of self.entityUrl after
         instantiation and discovery is complete.
        (*) Scenario:
            app = TentApp('http://foo.blogspot.com')
            Let's say that
                http://foo.blogspot.com
            has a <link> tag pointing to
                https://foo.tent.is/tent/profile
            We fetch foo.tent.is/profile and get new values for apiRootUrls and entityUrl:
                self.apiRootUrls = ['https://foo.tent.is/tent']
                self.entityUrl = 'https://foo.tent.is'
            Now self.entityUrl is not the same as the value that was
            passed into the constructor.
            This is a valid way of using your blogspot page as a kind of "tent redirect"
            to your real entityUrl, which will be "https://foo.tent.is".
            It's also possible that the server at tent.is would let you choose your own
            entityUrl, in which case you could choose your blogspot URL.  In that case,
            your entityUrl would be your blogspot URL.
            The entityUrl will be shown to other users in their Tent apps as a way of
            identifying you.
        """
        debugMain('init: entityUrl = %s'%entityUrl)

        self.entityUrl = entityUrl

        self.appDetails = {
            'name': 'python-tent-client',
            'description': 'description of my app',
            'url': 'http://zzzzexample.com',
            'icon': 'http://zzzzexample.com/icon.png',
            'oauthCallbackURL': 'http://zzzzexample.com/oauthcallback',
            'postNotificationUrl': None,
        }

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

        # keys. can contain:
        #   appID
        #   registration_mac_key
        #   registration_mac_key_id
        #   permanent_mac_key
        #   permanent_mac_key_id
        #   state
        self.keys = {}

        # this controls which keys are used by the auth hook
        # should be None, "registration", or "permanent"
        self.keysToUse = None

        # prepare a session for doing requests
        # we don't have auth keys yet, so make a non-auth session.
        # if authenticate is run later, this session will be replaced with a session that does authentication
        headers = dict(DEFAULT_HEADERS)
        headers['Host'] = urlparse(self.entityUrl).netloc
        self.session = requests.session(hooks={"pre_request": self._authHook}, headers=headers)

        # this list of api roots will be filled in by _discoverAPIurls()
        self.apiRootUrls = []
        self._discoverAPIUrls(self.entityUrl)

        # now that we've run discovery, the entityUrl might have changed
        # so we have to make a new session again.
        headers = dict(DEFAULT_HEADERS)
        headers['Host'] = urlparse(self.entityUrl).netloc
        self.session = requests.session(hooks={"pre_request": self._authHook}, headers=headers)


    #------------------------------------
    #--- misc helpers

    def hasRegistrationKeys(self):
        return bool(    'registration_mac_key' in self.keys    \
                    and 'registration_mac_key_id' in self.keys \
                    and 'appID' in self.keys )

    def hasPermanentKeys(self):
        return bool(    'permanent_mac_key' in self.keys \
                    and 'permanent_mac_key_id' in self.keys )

    def _authHook(self,req):
        # hook up sign_request() to be called on every request
        # using the current value of self.mac_key_id and self.mac_key

        if self.keysToUse == None:
            debugAuth('auth hook using no keys')
            return req
        elif self.keysToUse == 'permanent' and not self.hasPermanentKeys():
            debugAuth('auth hook could use permanent keys but there are none')
            return req
        elif self.keysToUse == 'permanent':
            debugAuth('auth hook using permanent keys')
            mac_key = self.keys['permanent_mac_key']
            mac_key_id = self.keys['permanent_mac_key_id']
        elif self.keysToUse == 'registration':
            debugAuth('auth hook using registration keys')
            mac_key = self.keys['registration_mac_key']
            mac_key_id = self.keys['registration_mac_key_id']
        else:
            1/0

        debugAuth('  mac key id: %s'%repr(mac_key_id))
        debugAuth('  mac key: %s'%repr(mac_key))

        parsed = urlparse(req.full_url)
        port = 80
        if parsed.scheme == "https": port = 443
        resource = parsed.path
        if parsed.query: resource = parsed.path + '?' + parsed.query
        req.headers['Authorization'] = buildHmacSha256AuthHeader(mac_key_id = mac_key_id,
                                                                 mac_key = mac_key,
                                                                 method = req.method,
                                                                 resource = resource,
                                                                 hostname = parsed.hostname,
                                                                 port = port)
        return req

    #------------------------------------
    #--- server discovery

    def _discoverAPIUrls(self,entityUrl):
        """set self.apiRootUrls, return None
        On failure, raise DiscoveryFailure
        """
        self.keysToUse = None

        # Will get Link headers or <link> pointers and put them in this list
        profileUrls = []

        # Get self.entityUrl doing just a HEAD request so we can get Link headers
        debugRequest('head request for discovery: %s'%entityUrl)
        r = retry(self.session.head,url=entityUrl)
        try:
            # Look in HTTP header for Link: foo; rel="$REL_PROFILE"
            # TODO: The requests API here only returns one link even when there are more than one in the
            #  header.  I think it returns the last one, but we should be using the first one.
            profileUrls = [ r.links['https://tent.io/rels/profile']['url'] ]
        except KeyError:
            # No Link header.  Have to look in the body for a <link> tag.
            try:
                debugRequest('get request for discovery: %s'%entityUrl)
                r = retry(self.session.get,url=entityUrl)
                links = r.text.split('<link')[1:]
                links = [link.split('>')[0] for link in links]
                links = [link for link in links if 'rel="https://tent.io/rels/profile"' in link]
                links = [link.split('href="')[1].split('"')[0] for link in links]
                profileUrls = [removeUnicode(link) for link in links]
            except IndexError:
                raise DiscoveryFailure() # couldn't find Link header or <link> tag

        # Convert relative profile urls to absolute.
        # This assumes they are relative to the entityUrl.
        # This is fragile right now because it assumes the entityUrl doesn't end with a slash.
        for ii in range(len(profileUrls)):
            if profileUrls[ii].startswith('/'):
                profileUrls[ii] = entityUrl + profileUrls[ii]

        debugDetail('profile URLs: %s'%profileUrls)

        # Hit the profile URL to get the official entityUrl and apiRootUrls
        debugRequest('get request to profile: %s'%profileUrls[0])
        # Can't use our session here because it has a hardcoded Host header
        # which points at the original entityUrl.
        # But now we want to get the profileUrl, which is maybe on a different host.
        r = retry(requests.get,profileUrls[0],headers=DEFAULT_HEADERS)
        profile = r.json
        self.entityUrl = removeUnicode(profile['https://tent.io/types/info/core/v0.1.0']['entity'])
        self.apiRootUrls = profile['https://tent.io/types/info/core/v0.1.0']['servers']
        self.apiRootUrls = [removeUnicode(url) for url in self.apiRootUrls]

        debugDetail('apiRootUrls = %s'%self.apiRootUrls)
        debugDetail('entityUrl = %s'%self.entityUrl)


    #------------------------------------
    #--- OAuth

    def register(self):
        """Register this app with the server.  This should only be done once for a given user.
        You can check if this has already happened by calling hasRegistrationKeys() to 
        check if this app's .keys have registration keys already.

        Preconditions for self.keys: none
        Sets in self.keys: appID, registration_mac_*
        On failure: raise RegistrationFailure
        Returns: None
        """
        debugMain('registering...')

        self.keysToUse = None

        # describe ourself to the server
        appInfoJson = {
            'name': self.appDetails['name'],
            'description': self.appDetails['description'],
            'url': self.appDetails['url'],
            'icon': self.appDetails['icon'],
            'redirect_uris': [self.appDetails['oauthCallbackURL']],
            'scopes': self.scopes,
        }
        debugJson(appInfoJson)

        # set up default headers for the session
        headers = dict(DEFAULT_HEADERS)
        headers['Content-Type'] = 'application/vnd.tent.v0+json'

        requestUrl = self.apiRootUrls[0] + '/apps'
        debugRequest('posting to %s'%requestUrl)
        r = retry(requests.post, requestUrl, data=json.dumps(appInfoJson), headers=headers)

        # get oauth key in response
        debugDetail('headers from server:')
        debugJson(r.headers)
        debugDetail('json from server:')
        debugJson(r.json)
        if r.json is None:
            debugError('not json.  here is the actual body text:')
            debugRaw(r.text)
            raise RegistrationFailure
        self.keys['appID'] = r.json['id'].encode('utf-8')
        self.keys['registration_mac_key_id'] = r.json['mac_key_id'].encode('utf-8')
        self.keys['registration_mac_key'] = r.json['mac_key'].encode('utf-8')
        debugDetail('registered successfully.  details:')
        debugDetail('  %s'%self.keys)


    def getUserApprovalURL(self):
        """Return a URL on the user's tent server that the user should visit
        to approve this app.  After approval the user will be redirected
        back to self.appDetails['oauthCallbackURL']

        Preconditions: app is registered already, aka self.hasRegistrationKeys()
        Preconditions for self.keys: appID, registration_mac_*
        Sets in self.keys: state
        On failure: cannot fail
        Returns: URL on tent server
        """
        debugMain('getting user approval URL...')

        assert self.hasRegistrationKeys()

        self.keys['state'] = randomString()

        # send user to the tent.is url to grant access
        # we will get the "code" in response
        params = {
            'client_id': self.keys['appID'],
            'redirect_uri': self.appDetails['oauthCallbackURL'],
            'state': self.keys['state'],
            'scope': ','.join(self.scopes.keys()),
            'tent_profile_info_types': 'all',
            'tent_post_types': 'all',
        }
        if self.appDetails.get('postNotificationURL',None):
            params['tent_notification_url'] = self.appDetails['postNotificationUrl']
        debugJson(params)
        requestUrl = self.apiRootUrls[0] + '/oauth/authorize'
        urlWithParams = requestUrl + '?' + urlencode(params)

        return urlWithParams


    def getPermanentKeys(self,code,state=None):
        """After the user has approved the app at their tent server, they'll be redirected
        to self.appDetails['oauthCallbackURL'] with a code and state provided by the tent server.
        Obtain those values and call this method to get permanent keys.
        State is optional.  If you provide it, it will be checked against the state we sent
        to the tent server in the first place.  If you omit it, that check will not be performed.

        Preconditions: app is registered already, aka self.hasRegistrationKeys()
        Preconditions for self.keys: appID, registration_mac_*, state
        Sets in self.keys: permanent_mac_*
        On failure: raise AuthRequestFailure
        Returns: None
        """
        debugMain('trading code for permanent keys...')
        self.keysToUse = 'registration'

        assert self.hasRegistrationKeys()
        if state and state != self.keys['state']:
            raise AuthRequestFailure # state we got back was different than the one we sent out

        # trade the code for a permanent key
        # first make the auth headers are using the credentials from the registration step
        resource = '/apps/%s/authorizations'%self.keys['appID']
        jsonPayload = {'code':code, 'token_type':'mac'}


        # then construct and send the request
        debugDetail()
        headers = dict(DEFAULT_HEADERS)
        headers['Content-Type'] = 'application/vnd.tent.v0+json'
        requestUrl = self.apiRootUrls[0] + resource
        debugRequest('posting to: %s'%requestUrl)
        r = retry(self.session.post, requestUrl, data=json.dumps(jsonPayload), headers=headers)

        # display our request
        debugDetail('request headers:')
        debugJson(r.request.headers)
        debugDetail('request data:')
        debugDetail(r.request.data)

        # then get the response
        debugDetail()
        debugDetail('response headers:')
        debugJson(r.headers)
        debugDetail('response text:')
        debugRaw(r.text)
        if not r.json:
            debugDetail()
            debugError('auth failed.')
            return
        debugJson(r.json)

        # now we have permanent keys
        self.keys['permanent_mac_key_id'] = r.json['access_token'].encode('utf-8')
        self.keys['permanent_mac_key'] = r.json['mac_key'].encode('utf-8')
        debugDetail('permanent mac key_id: %s'%self.keys['permanent_mac_key_id'])
        debugDetail('permanent mac key: %s'%self.keys['permanent_mac_key'])
        

    #------------------------------------
    #--- API methods

    def _genericGet(self,resource,**kwargs):
        """Do a get request using the provided kwargs as request parameters.
        """
        requestUrl = self.apiRootUrls[0] + resource
        debugRequest(requestUrl)
        r = retry(self.session.get,requestUrl,params=kwargs)
        if r.json is None:
            debugError('not json.  here is the actual body text:')
            debugRaw(r.text)
            return
        return r.json

    def getProfile(self):
        """Get your own profile.
        """
        # GET /profile
        self.keysToUse = 'permanent'
        debugMain('getProfile')
        return self._genericGet('/profile')

    def putProfile(profileType,value):
        """ Set a value for one of the profile types on your profile.
        TODO: not implemented yet.
        """
        # PUT /profile/$profileType
        self.keysToUse = 'permanent'
        pass
    
    def follow(self,entityUrl):
        """Begin following the given entity.
        Note that unlike the other follow-related methods, this one uses an entity URL
        instead of an id.
        """
        # POST /followings
        self.keysToUse = 'permanent'
        debugMain('follow')

        resource = '/followings'
        requestUrl = self.apiRootUrls[0] + resource
        headers = dict(DEFAULT_HEADERS)
        headers['Content-Type'] = 'application/vnd.tent.v0+json'
        debugRequest('following via: %s'%requestUrl)
        r = retry(self.session.post, requestUrl, data=json.dumps({'entity':entityUrl}), headers=headers)
        
        debugDetail('request headers:')
        debugJson(r.request.headers)
        debugDetail()
        debugDetail('request data:')
        debugRaw(r.request.data)
        debugDetail()
        debugDetail(' --  --  --  --')
        debugDetail()
        debugDetail('response headers:')
        debugJson(r.headers)
        debugDetail()
        debugDetail('response body:')
        debugRaw(r.text)
        debugDetail()
        
        if r.json is None:
            debugError('failed to follow.')
            debugDetail()
        return r.json

    def getFollowings(self,id=None,**kwargs):
        """Get the entities I'm following.
        Any additional keyword arguments will be passed to the server as request parameters.
        These ones are supported by tentd:
            limit       Max number to return; default to the max of 50
            before_id
            since_id
        """
        # GET /followings  [/$id]
        self.keysToUse = 'permanent'
        debugMain('getFollowings')
        if id is None:
            return self._genericGet('/followings',**kwargs)
        else:
            return self._genericGet('/followings/%s'%id,**kwargs)

    def unfollow(self,id):
        """Unfollow an entity.
        To get the id, you should first call followings() to get a list of entities and their ids.
        """
        # DELETE /followings/$id
        self.keysToUse = 'permanent'
        debugMain('unfollow')
        resource = '/followings/%s'%id
        requestUrl = self.apiRootUrls[0] + resource
        debugRequest('unfollowing: %s'%requestUrl)
        r = self.session.delete(requestUrl)
        
        debugDetail('request headers:')
        debugJson(r.request.headers)
        debugDetail()
        debugDetail(' --  --  --  --')
        debugDetail()
        debugDetail('response headers:')
        debugJson(r.headers)
        debugDetail()
        
        if r.status_code is not 200:
            debugError('failed to unfollow.')
            debugDetail()
            return False
        return True
        
    def getFollowers(self,id=None,**kwargs):
        """Get the entities who are following you.
        Any additional keyword arguments will be passed to the server as request parameters.
        These ones are supported by tentd:
            limit       Max number to return; default to the max of 50
            before_id
            since_id
        """
        self.keysToUse = 'permanent'
        # GET /followers  [/$id]
        debugMain('getFollowers')
        if id is None:
            return self._genericGet('/followers',**kwargs)
        else:
            return self._genericGet('/followers/%s'%id,**kwargs)

    def removeFollower(self,id):
        """Cause someone to stop following you?
        The docs are not clear on what this does.
        To get the id, you should first call followers() to get a list of entities and their ids.
        TODO: not implemented yet.
        """
        # DELETE /followers/$id
        self.keysToUse = 'permanent'
        pass

    def putPost(self,post,attachments=[]):
        """Post a new post to the server.
        post should be a python dictionary representing a JSON object
        See http://tent.io/docs/post-types for examples.
        TODO: Attachments are not implemented yet.
        """
        # POST /posts
        self.keysToUse = 'permanent'
        debugMain('putPost')

        resource = '/posts'
        requestUrl = self.apiRootUrls[0] + resource
        headers = dict(DEFAULT_HEADERS)
        headers['Content-Type'] = 'application/vnd.tent.v0+json'
        debugRequest('posting to: %s'%requestUrl)
        r = retry(self.session.post, requestUrl, data=json.dumps(post), headers=headers)

        debugDetail('request headers:')
        debugJson(r.request.headers)
        debugDetail()
        debugDetail('request data:')
        debugRaw(r.request.data)
        debugDetail()
        debugDetail(' --  --  --  --')
        debugDetail()
        debugDetail('response headers:')
        debugJson(r.headers)
        debugDetail()
        debugDetail('response body:')
        debugRaw(r.text)
        debugDetail()

        if r.json is None:
            debugError('failed to put post.')
            debugDetail()
        return r.json

    def getPosts(self,id=None,**kwargs):
        """With no auth, fetch your own public posts.
        With auth, fetch all your posts plus incoming posts from followings and people mentioning you.
        tent.is limits this to the last 50 posts or so unless additional parameters are present.
        Any additional keyword arguments will be passed to the server as request parameters.
        These ones are supported by tentd:
            limit             Max number to return; default to the max of 50
            before_id
            since_id
            before_id_entity  Use this if the before_id is not from one of your own posts
            since_id_entity   Use this if the since_id is not from one of your own posts
            before_time       Time should be an integer in Unix epoch format
            since_time
            entity            Posts published by the specified entity
            post_types        Filter down to these posts types (comma-separated type URIs)
        """
        # GET /posts  [/$id]
        self.keysToUse = 'permanent'
        debugMain('getPosts')
        if id is None:
            return self._genericGet('/posts',**kwargs)
        else:
            return self._genericGet('/posts/%s'%id,**kwargs)

    def getPostAttachment(self,id,filename):
        """Get an attachment from a post.
        TODO: not implemented yet.
        """
        # GET /posts/$id/attachments/$filename
        self.keysToUse = 'permanent'
        pass


    #------------------------------------
    #--- generators

    def _genericGenerator(self,method,**kwargs):
        oldestIdSoFar = None
        while True:
            if oldestIdSoFar is None:
                items = method(**kwargs)
            else:
                items = method(before_id=oldestIdSoFar,**kwargs)
            if not items:
                return
            for item in items:
                yield item
                oldestIdSoFar = item['id']
            time.sleep(0.5)

    def generatePosts(self,**kwargs):
        """Return a generator which iterates through all of the user's followers,
        newest first, making multiple GET requests behind the scenes.
        """
        self.keysToUse = 'permanent'
        oldestTimeSoFar = None
        while True:
            if oldestTimeSoFar is None:
                items = self.getPosts(**kwargs)
            else:
                items = self.getPosts(before_time=oldestTimeSoFar,**kwargs)
            if not items:
                return
            for item in items:
                yield item
                oldestTimeSoFar = item['published_at']
            time.sleep(0.5)

    def generateFollowings(self):
        """Return a generator which iterates through all of the user's followers,
        newest first, making multiple GET requests behind the scenes.
        """
        self.keysToUse = 'permanent'
        for f in self._genericGenerator(self.getFollowings):
            yield f

    def generateFollowers(self):
        """Return a generator which iterates through all of the user's followers,
        newest first, making multiple GET requests behind the scenes.
        """
        self.keysToUse = 'permanent'
        for f in self._genericGenerator(self.getFollowers):
            yield f
            
    #------------------------------------
    #--- helpers

    def authorizeFromCommandLine(self,keyStoreFilename):
        """This is a convenience method to set up auth for a command line script
        using a KeyStore file.  It will go through all the auth steps needed, including
        asking the user to approve the app the first time it's run.
        It will automatically load and save keys to the keystore.
        To use:
            app = TentApp('https://foo.tent.is')
            app.commandLineAuthHelper('keystore.js')
        """
        # Load auth keys from disk if they've been previously saved
        keyStore = KeyStore(keyStoreFilename)
        self.keys = keyStore.get(self.entityUrl, {})

        # Note that self.appDetails['oauthCallbackURL'] must be set before registering.
        # This is an URL for our app that the Tent server will redirect users to after
        # they approve our app.
        #     self.appDetails['oauthCallbackURL'] = 'http://zzzzexample.com/oauthcallback'

        # If the app has never been registered with the server, register now
        if not self.hasRegistrationKeys():
            self.register()
            keyStore.save(self.entityUrl, self.keys)

        # Ask the user to approve our app at their Tent server.
        # After that, they'll be redirected to our callback URL.
        # If they've already approved the app (and are logged in),
        # they will be instantly redirected back to our callback URL.
        if not self.hasPermanentKeys():
            approvalURL = self.getUserApprovalURL()
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
            self.getPermanentKeys(code)
            keyStore.save(self.entityUrl, self.keys)


