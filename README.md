python-tent-client
==================

A command-line client for talking to [Tent](http://tent.io/) servers such as [tent.is](https://tent.is/).

Current status
--------------

Things are rapidly changing.

What works:
* Discovery of the tent server's API root using link headers
* Registering an app with the server and requesting permissions using OAuth
* API methods that don't require authentication
* API methods that do require authentication
* Auth keys are saved to a local config file

What needs attention:
* Some API methods which require authentication have not been written yet
* Find elegant ways to deal with the JSON we get back from the Tent server.  Maybe add some classes representing posts, profiles, etc.
* Write tests
* Error handling
* Remove obnoxiously colorful debug output

It should be possible to register a notification url using this code, but since it's not necessarily running a webserver it won't be able to be notified of incoming posts.  Instead, you'll have to poll for new updates.

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

app = tentapp.TentApp("https://yourname.tent.is")

app.oauthRegister()  # Send the user to a browser asking them to approve the app.
                     # Tokens will be saved to "auth.cfg" and reused next time.

# Get your profile info as a JSON-style Python dictionary
print app.getProfile()

# Post a new post.  For now you need to supply the JSON dictionary yourself.
app.putPost(yourPostJsonHere)
```

You'll need to work directly with the JSON types described here: http://tent.io/docs/app-server


