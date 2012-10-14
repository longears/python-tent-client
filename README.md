python-tent-client
==================

A command-line client for talking to [Tent](http://tent.io/) servers such as [tent.is](https://tent.is/).

Current Status
--------------

We're in the "move fast and break things" phase right now.

What works:
* Discovery of the tent server's API root using link headers
* Registering an app with the server and requesting permissions using OAuth
* Auth keys are saved to a local config file for use next time
* API methods (both public ones and auth-requiring ones)

It should be possible to register a notification URL using this code, but since it's not necessarily running a webserver it won't be able to be notified of incoming posts.  In that case it can poll for new updates.

What needs attention:
* Some API methods have not been written yet.  Most of them should be quick to write by starting with copies of the methods that are already done.
* Write tests
* Error handling.  Should add a few exception types and also pay closer attention to errors from the `requests` module.
* Documentation
* Find elegant ways to deal with the JSON we get back from the Tent server.  Maybe add some classes representing posts, profiles, etc.
* Package this up as a real Python module that can be installed in the usual way

Dependencies
------------

* [requests](http://docs.python-requests.org/en/latest/#)

Installation of dependencies:

```
# get requests using pip
pip install requests

# you might already have an old version of requests that's missing the link headers feature.  If so:
pip install --update requests
```

Quick Start
-----------

Run `example.py` and it will launch your browser, have the Tent server ask you to approve the app, and then post a hello world message.  The OAuth process is awkward when run from a command line, so read the prompt when it asks you to copy and paste things from your browser.  You only have to do this once; after that your auth details are saved in 'auth.cfg' and reused in future runs.

`example_dashboard.py` will get your latest posts and followings' posts and print them to the shell.

Here's a quick overview:

```
import tentapp
tentapp.debug = False  # Turn this on if you want to see verbose debugging info while
                       # the app is running.  Defaults to False.


# "entity" is the Tent version of a username.  It's a full URL.
entityUrl = 'https://pythonclienttest.tent.is'
app = tentapp.TentApp(entityUrl)

# Get your profile info as a JSON-style Python dictionary
print app.getProfile()

# Send the user to their tent server to approve this app
# and save the resulting keys in a local file
app.authorizeFromCommandLine('keystore.js')

# Post a new post.  For now you need to supply the JSON dictionary yourself.
app.putPost(yourPostJsonHere)
```

You'll need to work directly with the JSON types described here: http://tent.io/docs/app-server


