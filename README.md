python-tent-client
==================

A command-line client for talking to [Tent](http://tent.io/) servers such as [tent.is](https://tent.is/)

Current status
--------------

Working:
* Discovery of the tent server's API root using link headers
* API methods that don't require authentication
* Registering an app up to the point where you need to start using MAC signatures, which is at the very end of that process

Not working:
* Authentication.  Something is wrong with the MAC signature, but I'm not sure what.  More details in [this issue report.](https://github.com/longears/python-tent-client/issues/1)

Not written yet:
* Persisting auth tokens after obtaining them
* Some API methods which require authentication
* Helper functions for dealing with the JSON we get back from the Tent server

Dependencies
------------

* [requests](http://docs.python-requests.org/en/latest/#)

How to use it
-------------

* Rename `myauthtokens.py.example` to `myauthtokens.py`.  In that file,
 * Set your username
 * Until we get the auth working, grab some auth tokens by viewing the source of your profile page on [tent.is](https://tent.is/).  Find the `mac_key` and `mac_key_id` and paste them into `myauthtokens.py`.  These are the tokens for tent.is's built-in "Tent Status" app.  Thanks to [elimisteve/clint](https://github.com/elimisteve/clint) for this trick.
* Use it like so.  There are more examples at the end of `tentapp.py`.

```
    import tentapp
    import myauthtokens
    app = tentapp.TentApp('http://%s.tent.is'%myauthtokens.username)
    print app.getProfile()
```

* When it works, authentication will look like this:

```
    app.oauth_register()    # Send the user to a browser asking them to approve the app
                            # After that, our secret key will be saved to a local config file
                            # and used for future calls requiring auth
    app.putPost(...)
```

