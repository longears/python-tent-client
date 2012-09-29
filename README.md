python-tent-client
==================

A command-line client for talking to [Tent](http://tent.io/) servers such as [tent.is](https://tent.is/).

Current status
--------------

What works:
* Discovery of the tent server's API root using link headers
* API methods that don't require authentication
* Registering an app
* Authentication
* Getting public posts; getting followers; posting statuses

What needs attention:
* Persist auth tokens locally after obtaining them
* Some API methods which require authentication have not been written yet
* Find elegant ways to deal with the JSON we get back from the Tent server.  Maybe add some classes representing posts, profiles, etc.
* Write tests
* Error handling
* Remove obnoxiously colorful debug output

Dependencies
------------

* [requests](http://docs.python-requests.org/en/latest/#)
* [macauthlib](https://github.com/mozilla-services/macauthlib)

How to use it
-------------

Set your username in `myauthtokens.py`.  You can leave the rest of that file alone for now.  Eventually we will be saving auto tokens there as they're generated.

For a quick start, run `tentapp.py` and it will launch your browser, ask you to approve it, and then post a hello world message.  The oauth process is awkward when run from a command line, so read the prompt when it asks you to copy and paste things from your browser.

There are some examples at the end of `tentapp.py`.  Here's a quick overview:

```
    import tentapp
    import myauthtokens

    app = tentapp.TentApp('http://%s.tent.is'%myauthtokens.username)
    app.oauth_register()    # Send the user to a browser asking them to approve the app
                            # We should, but currently do not, save the resulting auth keys 
                            # for future sessions, so each time this runs it will register as
                            # a new app.

    # Get your profile info as a JSON-style Python dictionary
    print app.getProfile()

    # Post a new post.  For now you need to supply the JSON dictionary yourself.
    app.putPost(yourPostJsonHere)
```

You'll need to work directly with the JSON types described here: http://tent.io/docs/app-server


