# coding=utf-8
from __future__ import unicode_literals
from reding import app
from .test_resources import ResourceTestCase
from . import rclient


class ReadMeTestCase(ResourceTestCase):
    def test(self):
        rclient.flushdb()
        self.app = app.app.test_client()
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
