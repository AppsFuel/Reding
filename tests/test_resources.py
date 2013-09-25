from __future__ import unicode_literals
import json
from unittest import TestCase
from reding import models, app, errors
from . import rclient
models.rclient = rclient


class ResourceTestCase(TestCase):
    def assertResponse(self, response, data, status=200, mimetype='application/json'):
        self.assertEqual(response.status_code, status)
        self.assertEqual(response.mimetype, mimetype)
        if status != 204:
            self.assertEqual(json.loads(response.data.decode('utf-8')), data)
        else:
            self.assertFalse(data)


class RatingDetailResourceTestCase(ResourceTestCase):
    def setUp(self):
        rclient.flushdb()
        self.app = app.app.test_client()
        self.model = models.RatingModel(namespace='test', user_id='ademarco', obj_id='reding')

    def test_get(self):
        self.model.set(5, 1379402591, param1=1, param2='two')
        response = self.app.get('/test/obj/reding/user/ademarco/')
        self.assertResponse(response, {
            'vote': 5,
            'user_id': 'ademarco',
            'when': 'Tue, 17 Sep 2013 09:23:11 -0000',
            'context': {'param1': '1', 'param2': 'two'},
            'object_id': 'reding',
            'opinions': [],
        })

    def test_get_notfound(self):
        response = self.app.get('/test/obj/reding/user/ademarco/')
        self.assertResponse(response, {
            'status': 404,
            'message': 'Not Found',
        }, status=404)

    def test_post(self):
        data = {
            'vote': 5,
            'param1': 1,
            'param2': 'two',
            'timestamp': 1379402591,
        }
        response = self.app.post('/test/obj/reding/user/ademarco/', data=data)
        self.assertResponse(response, {
            'vote': 5,
            'user_id': 'ademarco',
            'when': 'Tue, 17 Sep 2013 09:23:11 -0000',
            'context': {'param1': '1', 'param2': 'two'},
            'object_id': 'reding',
            'opinions': [],
        })
        self.assertEqual(self.model.get(), {
            'vote': 5.0,
            'when': 1379402591.0,
            'user_id': 'ademarco',
            'context': {'param1': '1', 'param2': 'two'},
            'object_id': 'reding',
            'opinions': [],
        })

    def test_delete(self):
        self.model.set(5, 1379402591, param1=1, param2='two')
        response = self.app.delete('/test/obj/reding/user/ademarco/')
        self.assertResponse(response, '', 204)
        self.assertRaises(errors.DoesNotExists, self.model.get)


class RatingListResourceTestCase(ResourceTestCase):
    def setUp(self):
        self.app = app.app.test_client()
        models.rclient.flushdb()
        for y in range(10):
            models.RatingModel(namespace='test', user_id='user_%d' % y, obj_id='obj_test').set(
                vote=y,
                timestamp=1379402590 - y,
                param1=y, param2=y ** 2
            )

    def test_get(self):
        response = self.app.get('/test/obj/obj_test/user/?vote_min=3&vote_max=4&size=1')
        self.assertResponse(response, [{
            'vote': 3,
            'user_id': 'user_3',
            'when': 'Tue, 17 Sep 2013 09:23:07 -0000',
            'context': {'param2': '9', 'param1': '3'},
            'object_id': 'obj_test',
            'opinions': [],
        }])

    def test_get_vote(self):
        response = self.app.get('/test/obj/obj_test/user/?vote_min=3&vote_max=4&size=1&sort=vote')
        self.assertResponse(response, [{
            'vote': 4,
            'user_id': 'user_4',
            'when': 'Tue, 17 Sep 2013 09:23:06 -0000',
            'context': {'param2': '16', 'param1': '4'},
            'object_id': 'obj_test',
            'opinions': [],
        }])


class ObjDetailResourceTestCase(ResourceTestCase):
    def setUp(self):
        models.rclient.flushdb()
        self.app = app.app.test_client()
        self.model = models.RatingModel(namespace='test', user_id='ademarco', obj_id='reding')

    def test_get(self):
        self.model.set(5, 1379402591, param1=1, param2='two')
        response = self.app.get('/test/obj/reding/')
        self.assertResponse(response, {
            'counters': [[5, 1]],
            'object_id': 'reding',
            'updated': 'Tue, 17 Sep 2013 09:23:11 -0000',
        })

    def test_get_notfound(self):
        response = self.app.get('/test/obj/reding/')
        self.assertResponse(response, {
            'status': 404,
            'message': 'Not Found',
        }, 404)


class ObjListResourceTestCase(ResourceTestCase):
    def setUp(self):
        self.app = app.app.test_client()
        models.rclient.flushdb()
        user = models.UserModel('test', 'ademarco')
        for y in range(10):
            models.ObjModel('test', 'obj_%d' % y).set(
                user=user,
                vote=y,
                timestamp=1379402590 - y,
            )

    def test_get(self):
        response = self.app.get('/test/obj/?size=1')
        self.assertResponse(response, [{
            'updated': 'Tue, 17 Sep 2013 09:23:01 -0000',
            'object_id': 'obj_9',
            'counters': [[9, 1]]
        }])

    def test_get_mostranked(self):
        response = self.app.get('/test/obj/?size=1')
        self.assertResponse(response, [{
            'updated': 'Tue, 17 Sep 2013 09:23:01 -0000',
            'object_id': 'obj_9',
            'counters': [[9, 1]]
        }])

    def test_get_lastupdated(self):
        response = self.app.get('/test/obj/?size=1&sort=updated')
        self.assertResponse(response, [{
            'updated': 'Tue, 17 Sep 2013 09:23:10 -0000',
            'object_id': 'obj_0',
            'counters': [[0, 1]]
        }])

    def test_get_filtered(self):
        response = self.app.get('/test/obj/?object_id=obj_3&object_id=obj_4')
        self.assertResponse(response, [
            {
                'updated': 'Tue, 17 Sep 2013 09:23:06 -0000',
                'object_id': 'obj_4',
                'counters': [[4, 1]]
            },
            {
                'updated': 'Tue, 17 Sep 2013 09:23:07 -0000',
                'object_id': 'obj_3',
                'counters': [[3, 1]]
            }
        ])
