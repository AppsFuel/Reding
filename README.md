Reding
======

[![Build Status](https://secure.travis-ci.org/BuongiornoMIP/Reding.png?branch=master)](https://travis-ci.org/BuongiornoMIP/Reding)
[![Coverage Status](https://coveralls.io/repos/BuongiornoMIP/Reding/badge.png?branch=master)](https://coveralls.io/r/BuongiornoMIP/Reding)
[![PyPi version](https://pypip.in/v/Reding/badge.png)](https://crate.io/packages/Reding/)
[![PyPi downloads](https://pypip.in/d/Reding/badge.png)](https://crate.io/packages/Reding/)

Rating on Redis - REST API on Flask
-----------------------------------
Reding is a *WSGI* Python app made using the amazing Flask web framework, and one of its extension, Flask-RESTful.

On Redis side, it uses the powerful sorted set data type to provide all the functionalities.


Installation:
-------------
```
pip install Reding
```


Some examples:
--------------
```python
# Let's start, my Reding is empty, no book has been voted. Note: `bookshelf` is my `namespace`.
response = self.app.get('/bookshelf/obj/')
self.assertResponse(response, [])
# I wanna give a '10' to the amazing 'Core Python Applications Programming' book (ISBN-13: 978-0132678209)
response = self.app.post('/bookshelf/obj/978-0132678209/user/gsalluzzo/', data={'vote': 10, 'timestamp': 1379402591})
self.assertResponse(response, {
    'opinions': [],
    'user_id': 'gsalluzzo',
    'when': 'Tue, 17 Sep 2013 09:23:11 -0000',
    'object_id': '978-0132678209',
    'context': {},
    'vote': 10
})
# OK, '10' is too much indeed, let's change it to '9' and add a review, or the author will get crazy about that
response = self.app.post('/bookshelf/obj/978-0132678209/user/gsalluzzo/', data={'vote': 9, 'timestamp': 1379402592, 'text': 'the ☃ loves python'})
self.assertResponse(response, {
    'opinions': [],
    'user_id': 'gsalluzzo',
    'when': 'Tue, 17 Sep 2013 09:23:12 -0000',
    'object_id': '978-0132678209',
    'context': {'text': 'the ☃ loves python'},
    'vote': 9
})
# Let's see if somebody voted something (my memory is like the gold fish one)
response = self.app.get('/bookshelf/obj/')
self.assertResponse(response, [{
    'updated': 'Tue, 17 Sep 2013 09:23:12 -0000',
    'object_id': '978-0132678209',
    'counters': [[9, 1]]
}])
# Not expected... ;) Let's enter another vote:
response = self.app.post('/bookshelf/obj/978-0132678209/user/wchun/', data={'vote': 10, 'timestamp': 1379402593})
self.assertResponse(response, {
    'opinions': [],
    'user_id': 'wchun',
    'when': 'Tue, 17 Sep 2013 09:23:13 -0000',
    'object_id': '978-0132678209',
    'context': {},
    'vote': 10
})
# The author said '10'! What a surprise! Let's get the voted books again
response = self.app.get('/bookshelf/obj/')
self.assertResponse(response, [{
    'updated': 'Tue, 17 Sep 2013 09:23:13 -0000',
    'object_id': '978-0132678209',
    'counters': [[10, 1], [9, 1]]
}])
#There's only a book, what if I only get that one??
response = self.app.get('/bookshelf/obj/978-0132678209/')
self.assertResponse(response, {
    'updated': 'Tue, 17 Sep 2013 09:23:13 -0000',
    'object_id': '978-0132678209',
    'counters': [[10, 1], [9, 1]]
})
#Or what if I only get my single vote?
response = self.app.get('/bookshelf/obj/978-0132678209/user/gsalluzzo/')
self.assertResponse(response, {
    'opinions': [],
    'user_id': 'gsalluzzo',
    'when': 'Tue, 17 Sep 2013 09:23:12 -0000',
    'object_id': '978-0132678209',
    'context': {'text': 'the ☃ loves python'},
    'vote': 9
})
# Let's remove the author's one, he cheated:
response = self.app.delete('/bookshelf/obj/978-0132678209/user/wchun/')
self.assertResponse(response, '', status=204)
# Let's enter my mom's vote, she does not like Python, she even doesn't know what it is...
response = self.app.post('/bookshelf/obj/978-0132678209/user/mymom/', data={'vote': 3, 'timestamp': 1379402594})
self.assertResponse(response, {
    'opinions': [],
    'user_id': 'mymom',
    'when': 'Tue, 17 Sep 2013 09:23:14 -0000',
    'object_id': '978-0132678209',
    'context': {},
    'vote': 3
})
# Of course, I don't agree with her: :thumbsdown:
response = self.app.post('/bookshelf:978-0132678209/obj/mymom/user/gsalluzzo/', data={'vote': -1, 'timestamp': 1379402595})
self.assertResponse(response, {
    'opinions': [],
    'user_id': 'gsalluzzo',
    'when': 'Tue, 17 Sep 2013 09:23:15 -0000',
    'object_id': 'mymom',
    'context': {},
    'vote': -1
})
# Now I marked her review with a :thumbsdown:
response = self.app.get('/bookshelf/obj/978-0132678209/user/mymom/')
self.assertResponse(response, {
    'opinions': [[-1, 1]],
    'user_id': 'mymom',
    'when': 'Tue, 17 Sep 2013 09:23:14 -0000',
    'object_id': '978-0132678209',
    'context': {},
    'vote': 3
})
```

Thanks to:
----------
* **Redis** project at http://redis.io/;
* **Flask** project at http://flask.pocoo.org/;
* **Flask-RESTful** project at https://github.com/twilio/flask-restful/;
* **CherryPy** project at http://cherrypy.org/ - if you wanna try it right now!;
* **Buongiorno S.p.A.** -my company-, letting me open sources to the world.


LICENSE
-------
The MIT License (MIT)

Copyright (c) 2013 Buongiorno S.p.A.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
