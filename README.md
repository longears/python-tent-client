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
* API methods that don't require authentication
* API methods that do require authentication

It should be possible to register a notification url using this code, but since it's not necessarily running a webserver it won't be able to be notified of incoming posts.  Instead, you'll have to poll for new updates.

What needs attention:
* Some API methods which require authentication have not been written yet
* Write tests
* Error handling.  Should add a few exception types and also pay closer attention to errors from the `requests` module.
* Find elegant ways to deal with the JSON we get back from the Tent server.  Maybe add some classes representing posts, profiles, etc.
* Documentation

Dependencies
------------

* [requests](http://docs.python-requests.org/en/latest/#)
* [macauthlib](https://github.com/mozilla-services/macauthlib) for MAC authentication.  There is some homegrown MAC code that may replace this dependency in the near future.

Installation of dependencies:

```
# get requests using pip
pip install requests

# you might already have an old version of requests that's missing the link headers feature.  If so:
pip install --update requests

# get macauthlib from GitHub (not pip; that version is old)
git clone git://github.com/mozilla-services/macauthlib.git
cd macauthlib
python setup.py install
cd ..
rm -rf macauthlib
```

Quick Start
-----------

Look in `example.py`.  Find `rabbitwhiskers.tent.is` and replace it with your Tent entity URL.

Run `example.py` and it will launch your browser, have the Tent server ask you to approve the app, and then post a hello world message.  The OAuth process is awkward when run from a command line, so read the prompt when it asks you to copy and paste things from your browser.  You only have to do this once; after that your auth details are saved in 'auth.cfg' and reused in future runs.

There are some other examples at the end of `tentapp.py`.  Here's a quick overview:

```
import tentapp

tentapp.debug = True  # Turn this on if you want to see verbose debugging info while
                      # the app is running.  Defaults to False.

app = tentapp.TentApp("https://yourname.tent.is")

# Get your profile info as a JSON-style Python dictionary
print app.getProfile()

app.oauthRegister()  # Send the user to a browser asking them to approve the app.
                     # Tokens will be saved to "auth.cfg" and reused next time.
                     # You can skip this if you just want to read public
                     # posts and profiles.

# Post a new post.  For now you need to supply the JSON dictionary yourself.
app.putPost(yourPostJsonHere)
```

You'll need to work directly with the JSON types described here: http://tent.io/docs/app-server


