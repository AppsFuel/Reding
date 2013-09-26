from collections import defaultdict
from uuid import uuid1


class ZRangeStore(object):
    def __init__(self, client):
        self.client = client

    def make_key(self, prefix='tmp', amount=1):
        for i in range(amount):
            yield '{0}:{1}'.format(prefix, uuid1())

    def bysubset(self, dest, zset, *items):
        if not items:
            self._clone(zset, dest)
            return
        tmp = self.make_key().next()
        self.client.sadd(tmp, *items)
        self.client.zinterstore(dest, {zset: 1, tmp: 0})
        self.client.delete(tmp)

    def byscore(self, dest, zset, m='-inf', M='+inf'):
        self._clone(zset, dest)
        if m is not None and m != '-inf':
            self.client.zremrangebyscore(dest, '-inf', '({0}'.format(m))
        if M is not None and M != '+inf':
            self.client.zremrangebyscore(dest, '({0}'.format(M), '+inf')

    def byrank(self, dest, zset, offset=0, size=None):
        self._clone(zset, dest)
        if offset:
            self.client.zremrangebyrank(dest, 0, offset - 1)
        if size:
            self.client.zremrangebyrank(dest, size, -1)

    def byrevrank(self, dest, zset, offset=0, size=None):
        self._clone(zset, dest)
        if offset:
            self.client.zremrangebyrank(dest, -offset, -1)
        if size:
            self.client.zremrangebyrank(dest, 0, -size - 1)

    def _clone(self, source, target):
        if source != target:
            self.client.zunionstore(dest=target, keys={source: 1})

    def intersect(self, *zsets):
        tmpzsets = list(self.make_key(amount=len(zsets)))
        for i, zset in enumerate(zsets):
            self.byscore(tmpzsets[i], zset['key'], m=zset.get('min', '-inf'), M=zset.get('max', '+inf'))
        self.client.zinterstore(tmpzsets[0], dict([(k, int(not i)) for i, k in enumerate(tmpzsets)]))
        return tmpzsets

    def slice(self, zset, offset=0, size=None, reverse=False, withscores=True):
        if not reverse:
            self.byrank(zset, zset, offset, size)
            x = self.client.zrange(zset, 0, -1, withscores=withscores)
        else:
            self.byrevrank(zset, zset, offset, size)
            x = self.client.zrevrange(zset, 0, -1, withscores=withscores)
        return x

    def leftintersect(self, left, right, withscores=True):
        self.client.zinterstore(left, {right: 0, left: 1})
        return self.client.zrange(left, 0, -1, withscores=withscores)

    def clear(self, *tmpzsets):
        self.client.delete(*tmpzsets)

    def sortnslice(self, zsets, offset=0, size=None, reverse=False, withscore=False):
        tmpzsets = self.intersect(*zsets)
        if not withscore:
            return self.slice(tmpzsets[0], offset, size, reverse, withscores=False)
        intersets = [self.slice(tmpzsets[0], offset, size, reverse)]
        for tmpzset in tmpzsets[1:]:
            t = self.leftintersect(tmpzset, tmpzsets[0], withscores=True)
            intersets.append(t)
        self.clear(*tmpzsets)
        return self.dictionarize(*intersets)

    @staticmethod
    def dictionarize(*intersets):
        tmp = defaultdict(list)
        for s in intersets:
            for k, v in s:
                tmp[k].append(v)
        return [{
            'key': key,
            'value': tuple(tmp[key])
        } for key in [e[0] for e in intersets[0]]]
