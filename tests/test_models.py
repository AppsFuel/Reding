from unittest import TestCase
from reding import models
from reding.errors import DoesNotExists
from . import rclient
models.rclient = rclient


class ObjModelTestCase(TestCase):
    def setUp(self):
        rclient.flushdb()
        self.obj = models.ObjModel('test', 'reding')
        self.user = models.UserModel('test', 'ademarco')
        self.obj.set(self.user, 5, 1379402591)

    def test_get(self):
        self.assertEqual(self.obj.get(), {
            'updated': 1379402591.0,
            'object_id': 'reding',
            'counters': [(5, 1)],
        })

    def test_vote(self):
        self.assertEqual(self.obj.vote(self.user), 5)

    def test_timestamp(self):
        self.assertEqual(self.obj.timestamp(self.user), 1379402591)

    def test_updated(self):
        self.assertEqual(self.obj.updated, 1379402591)

    def test_votemap(self):
        self.assertEqual(self.obj.votemap, [(5, 1)])

    def test_set(self):
        self.obj.set(self.user, 10, 1379402592)
        self.assertEqual(self.obj.vote(self.user), 10)
        self.assertEqual(self.obj.timestamp(self.user), 1379402592)
        self.assertEqual(self.obj.get(), {
            'updated': 1379402592.0,
            'object_id': 'reding',
            'counters': [(10, 1)],
        })

    def test_delete(self):
        self.obj.delete(self.user, timestamp=1379402592)
        self.assertEqual(self.obj.vote(self.user), None)
        self.assertEqual(self.obj.timestamp(self.user), None)
        self.assertRaises(DoesNotExists, self.obj.get)

    def test_set_and_delete(self):
        george = models.UserModel('test', 'gsalluzzo')
        self.obj.set(george, 10, 1379402592)
        self.assertEqual(self.obj.vote(george), 10)
        self.assertEqual(self.obj.timestamp(george), 1379402592)
        self.assertEqual(self.obj.get(), {
            'updated': 1379402592.0,
            'object_id': 'reding',
            'counters': [(5, 1), (10, 1)],
        })
        self.obj.delete(george, 1379402593)
        self.assertEqual(self.obj.vote(george), None)
        self.assertEqual(self.obj.timestamp(george), None)
        self.assertEqual(self.obj.get(), {
            'updated': 1379402593.0,
            'object_id': 'reding',
            'counters': [(5, 1)],
        })


class ObjModelDetailsTestCase(TestCase):
    def setUp(self):
        models.rclient.flushdb()
        for y in range(10):
            models.RatingModel(namespace='test', user_id='user_%d' % y, obj_id='obj_test').set(
                vote=y,
                timestamp=1379402590 - y,
                param1=y, param2=y ** 2
            )
        self.obj = models.ObjModel('test', 'obj_test')

    def test_details(self):
        self.assertEqual(self.obj.details(vote_min=3, vote_max=4, size=1), [{
            'vote': 3.0,
            'when': 1379402587.0,
            'user_id': 'user_3',
            'context': {'param2': '9', 'param1': '3'},
            'object_id': 'obj_test',
            'opinions': [],
        }])

    def test_details_vote(self):
        self.assertEqual(self.obj.details(vote_min=3, vote_max=4, size=1, sort_key='vote'), [{
            'vote': 4.0,
            'when': 1379402586.0,
            'user_id': 'user_4',
            'context': {'param2': '16', 'param1': '4'},
            'object_id': 'obj_test',
            'opinions': [],
        }])

    def test_details_empty_opinions(self):
        self.assertEqual(self.obj.details(vote_min=3, vote_max=4, size=1, sort_key='opinions'), [{
            'vote': 3.0,
            'when': 1379402587.0,
            'user_id': 'user_3',
            'context': {'param2': '9', 'param1': '3'},
            'object_id': 'obj_test',
            'opinions': [],
        }])

    def test_details_opinions(self):
        models.RatingModel(namespace='test:obj_test', obj_id='user_4', user_id='user_3', ).set(vote=1, timestamp=1379402590)
        models.RatingModel(namespace='test:obj_test', obj_id='user_4', user_id='user_5', ).set(vote=1, timestamp=1379402591)
        models.RatingModel(namespace='test:obj_test', obj_id='user_4', user_id='user_6', ).set(vote=-1, timestamp=1379402592)
        self.assertEqual(self.obj.details(vote_min=3, vote_max=4, size=1, sort_key='opinions'), [{
            'vote': 4.0,
            'when': 1379402586.0,
            'user_id': 'user_4',
            'context': {'param2': '16', 'param1': '4'},
            'object_id': 'obj_test',
            'opinions': [(-1, 1), (1, 2)],
        }])

    def test_details_opinions_badsort(self):
        self.assertRaises(DoesNotExists, self.obj.details, sort_key='errors')


class RatingModelTestCase(TestCase):
    def setUp(self):
        models.rclient.flushdb()
        self.model = models.RatingModel(namespace='test', user_id='ademarco', obj_id='reding')
        self.model.set(5, 1379402591, param1=1, param2='two')

    def test_get(self):
        self.assertEqual(self.model.get(), {
            'vote': 5.0,
            'when': 1379402591.0,
            'user_id': 'ademarco',
            'context': {'param2': 'two', 'param1': '1'},
            'object_id': 'reding',
            'opinions': [],
        })

    def test_delete(self):
        self.model.delete(1379402591)
        self.assertRaises(DoesNotExists, self.model.get)


class ObjManagerTestCase(TestCase):
    def setUp(self):
        models.rclient.flushdb()
        self.manager = models.ObjManager('test')
        user = models.UserModel('test', 'ademarco')
        for y in range(10):
            models.ObjModel('test', 'obj_%d' % y).set(
                user=user,
                vote=y,
                timestamp=1379402590 - y,
            )

    def test_get_mostranked(self):
        self.assertEqual(self.manager.list(size=1), [{
            'updated': 1379402581.0,
            'object_id': 'obj_9',
            'counters': [(9, 1)]
        }])

    def test_get_lastupdated(self):
        self.assertEqual(self.manager.list(size=1, sort_key='updated'), [{
            'updated': 1379402590.0,
            'object_id': 'obj_0',
            'counters': [(0, 1)],
        }])

    def test_get_filtered(self):
        self.assertEqual(self.manager.list(objects_id=('obj_3', 'obj_4')), [
            {'updated': 1379402586.0, 'object_id': 'obj_4', 'counters': [(4, 1)]},
            {'updated': 1379402587.0, 'object_id': 'obj_3', 'counters': [(3, 1)]},
        ])

    def test_list_ids(self):
        self.assertEqual(
            self.manager.list_ids(size=3, sort_key='updated'),
            ['obj_0', 'obj_1', 'obj_2'],
        )
