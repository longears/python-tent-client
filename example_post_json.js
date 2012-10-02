Actual JSON objects from the tent.is API.
Missing so far:
    Profile of another person using your own authentication
    Repost with no auth
    Delete with auth
    Posts with attachments
    Photo, Essay, Album
    Notification messages (see https://github.com/tent/tent.io/issues/92)
    Groups, eventually
    Views (see http://tent.io/docs/post-types)


--- PROFILE (your own profile, with authentication) ---
{
    "https://tent.io/types/info/basic/v0.1.0": {
        "avatar_url": "https://twimg0-a.akamaihd.net/profile_images/1661050796/rabbit_egg_pixel_4x.png", 
        "bio": "This account is old; please use longears.tent.is instead.  Berkeley, CA. Developer of https://github.com/longears/python-tent-client", 
        "birthdate": "", 
        "gender": "", 
        "location": "", 
        "name": "Rabbit Whiskers", 
        "permissions": {
            "entities": {}, 
            "groups": [], 
            "public": true
        }
    }, 
    "https://tent.io/types/info/core/v0.1.0": {
        "entity": "https://rabbitwhiskers.tent.is", 
        "licenses": [], 
        "permissions": {
            "entities": {}, 
            "groups": [], 
            "public": true
        }, 
        "servers": [
            "https://rabbitwhiskers.tent.is/tent"
        ]
    }
}


--- PROFILE (no auth) ---
{
    "https://tent.io/types/info/basic/v0.1.0": {
        "avatar_url": "https://twimg0-a.akamaihd.net/profile_images/1661050796/rabbit_egg_pixel_4x.png", 
        "bio": "This account is old; please use longears.tent.is instead.  Berkeley, CA. Developer of https://github.com/longears/python-tent-client", 
        "birthdate": "", 
        "gender": "", 
        "location": "", 
        "name": "Rabbit Whiskers", 
        "permissions": {
            "public": true
        }
    }, 
    "https://tent.io/types/info/core/v0.1.0": {
        "entity": "https://rabbitwhiskers.tent.is", 
        "licenses": [], 
        "permissions": {
            "public": true
        }, 
        "servers": [
            "https://rabbitwhiskers.tent.is/tent"
        ]
    }
}


--- FOLLOWING (no auth) ---
{
    "entity": "https://redskyforge.tent.is", 
    "id": "mlf0bb", 
    "permissions": {
        "public": true
    }, 
    "remote_id": "ag6u4p"
}


--- FOLLOWING (auth) ---
{
    "created_at": 1349115363, 
    "entity": "https://redskyforge.tent.is", 
    "groups": [], 
    "id": "mlf0bb", 
    "licenses": [], 
    "permissions": {
        "entities": {}, 
        "groups": [], 
        "public": true
    }, 
    "profile": {
        "https://tent.io/types/info/basic/v0.1.0": {
            "avatar_url": "https://si0.twimg.com/profile_images/2609036383/h3jgsk4sxozfp5ihop0d_reasonably_small.jpeg", 
            "bio": "Freelance web and mobile developer. Tent evangelist.", 
            "birthdate": "", 
            "gender": "", 
            "location": "The Netherlands", 
            "name": "Dave Clayton", 
            "permissions": {
                "public": true
            }
        }, 
        "https://tent.io/types/info/core/v0.1.0": {
            "entity": "https://redskyforge.tent.is", 
            "licenses": [], 
            "permissions": {
                "public": true
            }, 
            "servers": [
                "https://redskyforge.tent.is/tent"
            ]
        }
    }, 
    "remote_id": "ag6u4p", 
    "updated_at": 1349159607
}


--- FOLLOWER (no auth) ---
{
    "entity": "https://jamieforrest.tent.is", 
    "id": "z3p07t", 
    "permissions": {
        "public": true
    }
}


--- FOLLOWER (auth) ---
{
    "created_at": 1349151723, 
    "entity": "https://jamieforrest.tent.is", 
    "groups": [], 
    "id": "z3p07t", 
    "licenses": [], 
    "permissions": {
        "entities": {}, 
        "groups": [], 
        "public": true
    }, 
    "profile": {
        "https://tent.io/types/info/basic/v0.1.0": {
            "avatar_url": "http://www.gravatar.com/avatar/580f40f60387ac6ababbfc60550a03b5.png", 
            "bio": "Co-founder of AnswerQi. I like building stuff for the web and iOS.", 
            "birthdate": "", 
            "gender": "", 
            "location": "Pittsburgh, PA", 
            "name": "Jamie Forrest", 
            "permissions": {
                "public": true
            }
        }, 
        "https://tent.io/types/info/core/v0.1.0": {
            "entity": "https://jamieforrest.tent.is", 
            "licenses": [], 
            "permissions": {
                "public": true
            }, 
            "servers": [
                "https://jamieforrest.tent.is/tent"
            ]
        }
    }, 
    "types": [
        "all"
    ], 
    "updated_at": 1349154081
}


--- POST: profile (no auth) ---
{
    "app": {
        "name": null, 
        "url": null
    }, 
    "attachments": [], 
    "content": {
        "action": "update", 
        "types": [
            "https://tent.io/types/info/basic/v0.1.0"
        ]
    }, 
    "entity": "https://rabbitwhiskers.tent.is", 
    "id": "aix8qk", 
    "licenses": [], 
    "mentions": [], 
    "permissions": {
        "public": true
    }, 
    "published_at": 1349154118, 
    "type": "https://tent.io/types/post/profile/v0.1.0", 
    "version": 2
}


--- POST: status (no auth) ---
{
    "app": {
        "name": "TentStatus", 
        "url": "https://apps.tent.is/status"
    }, 
    "attachments": [], 
    "content": {
        "text": "Hey other devs, I'm moving to a new account: ^longears.  Follow me there?\r\n\r\n^daniel ^jamieforrest ^songgao ^tent ^elimisteve ^followben ^jonathan ^jyap"
    }, 
    "entity": "https://rabbitwhiskers.tent.is", 
    "id": "ymq0yg", 
    "licenses": [], 
    "mentions": [
        {
            "entity": "https://longears.tent.is"
        }, 
        {
            "entity": "https://daniel.tent.is"
        }, 
        {
            "entity": "https://jamieforrest.tent.is"
        }, 
        {
            "entity": "https://songgao.tent.is"
        }, 
        {
            "entity": "https://tent.tent.is"
        }, 
        {
            "entity": "https://elimisteve.tent.is"
        }, 
        {
            "entity": "https://followben.tent.is"
        }, 
        {
            "entity": "https://jonathan.tent.is"
        }, 
        {
            "entity": "https://jyap.tent.is"
        }
    ], 
    "permissions": {
        "public": true
    }, 
    "published_at": 1349153057, 
    "type": "https://tent.io/types/post/status/v0.1.0", 
    "version": 1
}


--- POST: status (auth) ---
{
    "app": {
        "name": "TentStatus", 
        "url": "https://apps.tent.is/status"
    }, 
    "attachments": [], 
    "content": {
        "text": "^swansinflight ^rabbitwhiskers Oops, thanks :)"
    }, 
    "entity": "https://longears.tent.is", 
    "id": "a7t3bf", 
    "licenses": [], 
    "mentions": [
        {
            "entity": "https://swansinflight.tent.is", 
            "post": "eqnth4"
        }, 
        {
            "entity": "https://rabbitwhiskers.tent.is"
        }
    ], 
    "permissions": {
        "entities": {}, 
        "groups": [], 
        "public": true
    }, 
    "published_at": 1349170604, 
    "received_at": 1349170603, 
    "type": "https://tent.io/types/post/status/v0.1.0", 
    "updated_at": 1349170603, 
    "version": 1
}


--- POST: delete (no auth) ---
{
    "app": {
        "name": null, 
        "url": null
    }, 
    "attachments": [], 
    "content": {
        "id": "4xl58k"
    }, 
    "entity": "https://rabbitwhiskers.tent.is", 
    "id": "otbgt0", 
    "licenses": [], 
    "mentions": [], 
    "permissions": {
        "public": true
    }, 
    "published_at": 1349137921, 
    "type": "https://tent.io/types/post/delete/v0.1.0", 
    "version": 2
}


--- POST: repost (auth) ---
{
    "app": {
        "name": "TentStatus", 
        "url": "https://apps.tent.is/status"
    }, 
    "attachments": [], 
    "content": {
        "entity": "https://graue.tent.is", 
        "id": "ic7yue"
    }, 
    "entity": "https://elimisteve.tent.is", 
    "following_id": "mwnjnv", 
    "id": "wmw9xd", 
    "licenses": [], 
    "mentions": [], 
    "permissions": {
        "entities": {}, 
        "groups": [], 
        "public": true
    }, 
    "published_at": 1349167549, 
    "received_at": 1349167550, 
    "type": "https://tent.io/types/post/repost/v0.1.0", 
    "updated_at": 1349167550, 
    "version": 1
}


