from __future__ import unicode_literals
from unittest import TestCase
from reding.queries import ZRangeStore
from . import rclient


class RangeQueryTestCase(TestCase):
    def setUp(self):
        self.zset = 'test:zset:x'
        self.dest = 'test:zset:x:tmp'
        rclient.flushdb()
        rclient.zadd(self.zset, **dict([('p{0}'.format(x), x) for x in range(10)]))
        self.zrangestore = ZRangeStore(rclient)

    def test_zrangebysubsetstore(self):
        self.zrangestore.bysubset(self.dest, self.zset, 'p0', 'p2', 'p8')
        self.assertEqual(
            rclient.zrange(self.dest, 0, -1, withscores=True),
            [('p0', 0.0), ('p2', 2.0), ('p8', 8.0)]
        )

    def test_zrangebysubsetstore_all(self):
        self.zrangestore.bysubset(self.dest, self.zset)
        self.assertEqual(
            rclient.zrange(self.dest, 0, -1, withscores=True),
            rclient.zrange(self.zset, 0, -1, withscores=True)
        )

    def test_zrangebyscorestore(self):
        self.zrangestore.byscore(self.dest, self.zset)
        self.assertEqual(
            rclient.zrange(self.dest, 0, -1, withscores=True),
            rclient.zrange(self.zset, 0, -1, withscores=True)
        )

    def test_zrangebyscorestore_min(self):
        self.zrangestore.byscore(self.dest, self.zset, m=5)
        self.assertEqual(
            rclient.zrange(self.dest, 0, -1, withscores=True),
            [('p5', 5.0), ('p6', 6.0), ('p7', 7.0), ('p8', 8.0), ('p9', 9.0)]
        )

    def test_zrangebyscorestore_max(self):
        self.zrangestore.byscore(self.dest, self.zset, M=5)
        self.assertEqual(
            rclient.zrange(self.dest, 0, -1, withscores=True),
            [('p0', 0.0), ('p1', 1.0), ('p2', 2.0), ('p3', 3.0), ('p4', 4.0), ('p5', 5.0)]
        )

    def test_zrangebyscorestore_minmax(self):
        self.zrangestore.byscore(self.dest, self.zset, m=2, M=5)
        self.assertEqual(
            rclient.zrange(self.dest, 0, -1, withscores=True),
            [('p2', 2.0), ('p3', 3.0), ('p4', 4.0), ('p5', 5.0)]
        )

    def test_zrangebyscorestore_minmax_eq(self):
        self.zrangestore.byscore(self.dest, self.zset, m=5, M=5)
        self.assertEqual(
            rclient.zrange(self.dest, 0, -1, withscores=True),
            [('p5', 5.0)]
        )

    def test_zrangebyrankstore(self):
        self.zrangestore.byrank(self.dest, self.zset)
        self.assertEqual(
            rclient.zrange(self.dest, 0, -1, withscores=True),
            rclient.zrange(self.zset, 0, -1, withscores=True)
        )

    def test_zrangebyrankstore_offset(self):
        self.zrangestore.byrank(self.dest, self.zset, offset=8)
        self.assertEqual(
            rclient.zrange(self.dest, 0, -1, withscores=True),
            [('p8', 8.0), ('p9', 9.0)]
        )

    def test_zrangebyrankstore_size(self):
        self.zrangestore.byrank(self.dest, self.zset, size=2)
        self.assertEqual(
            rclient.zrange(self.dest, 0, -1, withscores=True),
            [('p0', 0.0), ('p1', 1.0)]
        )

    def test_zrangebyrankstore_offsetsize(self):
        self.zrangestore.byrank(self.dest, self.zset, offset=3, size=3)
        self.assertEqual(
            rclient.zrange(self.dest, 0, -1, withscores=True),
            [('p3', 3.0), ('p4', 4.0), ('p5', 5.0)]
        )

    def test_zrevrangebyrankstore(self):
        self.zrangestore.byrevrank(self.dest, self.zset)
        self.assertEqual(
            rclient.zrange(self.dest, 0, -1, withscores=True),
            rclient.zrange(self.zset, 0, -1, withscores=True)
        )

    def test_zrevrangebyrankstore_offset(self):
        self.zrangestore.byrevrank(self.dest, self.zset, offset=8)
        self.assertEqual(
            rclient.zrange(self.dest, 0, -1, withscores=True),
            [('p0', 0.0), ('p1', 1.0)]
        )

    def test_zrevrangebyrankstore_size(self):
        self.zrangestore.byrevrank(self.dest, self.zset, size=2)
        self.assertEqual(
            rclient.zrange(self.dest, 0, -1, withscores=True),
            [('p8', 8.0), ('p9', 9.0)]
        )

    def test_zrevrangebyrankstore_offsetsize(self):
        self.zrangestore.byrevrank(self.dest, self.zset, offset=3, size=3)
        self.assertEqual(
            rclient.zrange(self.dest, 0, -1, withscores=True),
            [('p4', 4.0), ('p5', 5.0), ('p6', 6.0)]
        )

    def test_slice(self):
        self.assertEqual(
            self.zrangestore.slice(self.zset, offset=3, size=3),
            [('p3', 3.0), ('p4', 4.0), ('p5', 5.0)]
        )

    def test_slice_reverse(self):
        self.assertEqual(
            self.zrangestore.slice(self.zset, offset=3, size=3, reverse=True),
            [('p6', 6.0), ('p5', 5.0), ('p4', 4.0)]
        )


class ApiTestCase(TestCase):
    def setUp(self):
        rclient.flushdb()
        for x in range(10):
            for y in range(10):
                name = 'P{0}'.format(x * 10 + y)
                rclient.zadd('zset_x', x, name)
                rclient.zadd('zset_y', y, name)
        self.zrangestore = ZRangeStore(rclient)

    def test_withscore(self):
        got = self.zrangestore.sortnslice([
            {
                'key': 'zset_x',
                'min': 3,
                'max': 8,
            },
            {
                'key': 'zset_y',
                'min': 2,
                'max': 5,
            },
        ], offset=0, size=3, reverse=True, withscore=True)
        self.assertEqual(got, [{'value': (8.0, 5.0), 'key': 'P85'}, {'value': (8.0, 4.0), 'key': 'P84'}, {'value': (8.0, 3.0), 'key': 'P83'}])

    def test_indexes(self):
        got = self.zrangestore.sortnslice([
            {
                'key': 'zset_x',
                'min': 3,
                'max': 8,
            },
            {
                'key': 'zset_y',
                'min': 2,
                'max': 5,
            },
        ], offset=0, size=3, reverse=True)
        self.assertEqual(got, ['P85', 'P84', 'P83'])
