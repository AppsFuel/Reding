import time
from reding.errors import DoesNotExists
from reding.queries import ZRangeStore
import redis
from flask.ext.restful import fields
from reding.settings import REDIS_CONFIG
from reding import fields as rfields
rclient = redis.StrictRedis(**REDIS_CONFIG)


class ObjManager(object):
    def __init__(self, namespace):
        self.namespace = namespace
        self.zsumvotes = '{prefix}:obj:zsumvotes'.format(prefix=namespace)
        self.zupdated = '{prefix}:obj:zupdated'.format(prefix=namespace)

    def list(self, objects_id=None, offset=None, size=None, amount_min='-inf', amount_max='+inf', updated_min='-inf', updated_max='+inf', sort_key='amount', sort_desc=True):
        return [
            ObjModel(namespace=self.namespace, obj_id=obj_id).get()
            for obj_id in self.list_ids(objects_id, offset, size, amount_min, amount_max, updated_min, updated_max, sort_key, sort_desc)
        ]

    def list_ids(self, objects_id=None, offset=None, size=None, amount_min='-inf', amount_max='+inf', updated_min='-inf', updated_max='+inf', sort_key='amount', sort_desc=True):
        zrangestore = ZRangeStore(rclient)
        amount_item = {
            'key': self.zsumvotes,
            'min': amount_min,
            'max': amount_max,
        }
        updated_item = {
            'key': self.zupdated,
            'min': updated_min,
            'max': updated_max,
        }
        zsets = {'updated': (updated_item, amount_item), 'amount': (amount_item, updated_item)}[sort_key]
        if objects_id:
            newkey = zrangestore.make_key()
            zrangestore.bysubset(newkey, zsets[0]['key'], *objects_id)
            zsets[0]['key'] = newkey
        return zrangestore.sortnslice(zsets, offset=offset, size=size, reverse=sort_desc)


class ObjModel(object):
    fields = {
        'counters': fields.Raw,
        'object_id': fields.String,
        'updated': rfields.DateTimestamp,
    }

    def __init__(self, namespace, obj_id):
        self.namespace = namespace
        self.identifier = obj_id
        self.manager = ObjManager(namespace=namespace)
        self.opinion_manager = ObjManager(namespace='{0}:{1}'.format(namespace, obj_id))
        self.zcounters = '{prefix}:obj:{obj_id}:hcounters'.format(prefix=namespace, obj_id=obj_id)
        self.zvotes = '{prefix}:obj:{obj_id}:zvotes'.format(prefix=namespace, obj_id=obj_id)
        self.ztimestamps = '{prefix}:obj:{obj_id}:zts'.format(prefix=namespace, obj_id=obj_id)

    def set(self, user, vote, timestamp):
        vote = float(vote)
        user_vote = self.vote(user)
        rclient.zadd(self.zvotes, vote, user.identifier)
        rclient.zadd(self.ztimestamps, timestamp, user.identifier)
        if user_vote is not None and not rclient.hincrby(name=self.zcounters, key=user_vote, amount=-1):
            rclient.hdel(self.zcounters, user_vote)
        rclient.hincrby(name=self.zcounters, key=vote)
        rclient.zincrby(name=self.manager.zsumvotes, value=self.identifier, amount=vote - (user_vote or 0))
        rclient.zadd(self.manager.zupdated, timestamp, self.identifier)

    def get(self):
        votemap = self.votemap
        if not votemap:
            raise DoesNotExists()
        return {
            'counters': votemap,
            'updated': self.updated,
            'object_id': self.identifier,
        }

    def delete(self, user, timestamp):
        user_vote = self.vote(user)
        rclient.zrem(self.zvotes, user.identifier)
        rclient.zrem(self.ztimestamps, user.identifier)
        if not rclient.zcount(self.zvotes, '-inf', '+inf'):
            rclient.delete(self.zcounters)
            rclient.zrem(self.manager.zsumvotes, self.identifier)
        elif user_vote is not None:
            rclient.zincrby(name=self.manager.zsumvotes, value=self.identifier, amount=-(user_vote or 0))
            if not rclient.hincrby(name=self.zcounters, key=user_vote, amount=-1):
                rclient.hdel(self.zcounters, user_vote)
        rclient.zadd(self.manager.zupdated, timestamp, self.identifier)

    def vote(self, user):
        return rclient.zscore(name=self.zvotes, value=user.identifier)

    def timestamp(self, user):
        return rclient.zscore(name=self.ztimestamps, value=user.identifier)

    @property
    def votemap(self):
        return [(int(float(k)), int(v)) for k, v in rclient.hgetall(self.zcounters).items()]

    @property
    def updated(self):
        return rclient.zscore(name=self.manager.zupdated, value=self.identifier)

    def details(self, offset=None, size=None, vote_min='-inf', vote_max='+inf', when_min='-inf', when_max='+inf', sort_key='when', sort_desc=True):
        zrangestore = ZRangeStore(rclient)
        vote_item = {
            'key': self.zvotes,
            'min': vote_min,
            'max': vote_max,
        }
        when_item = {
            'key': self.ztimestamps,
            'min': when_min,
            'max': when_max,
        }
        if sort_key in ('when', 'vote'):
            users = zrangestore.sortnslice(
                zsets={'when': (when_item, vote_item), 'vote': (vote_item, when_item)}[sort_key],
                offset=offset,
                size=size,
                reverse=sort_desc,
            )
        elif sort_key in ('opinions',):
            sliced = zrangestore.sortnslice((when_item, vote_item))
            users = self.opinion_manager.list_ids(
                objects_id=zrangestore.sortnslice((when_item, vote_item)),
                offset=offset,
                size=size,
                sort_desc=sort_desc
            )
            users.extend(set(sliced) - set(users))
            users = users[:size]
        else:
            raise DoesNotExists()
        return [
            RatingModel(namespace=self.namespace, obj_id=self.identifier, user_id=user_id).get()
            for user_id in users
        ]


class UserModel(object):
    def __init__(self, namespace, user_id):
        self.identifier = user_id


class RatingModel(object):
    fields = {
        'vote': fields.Integer,
        'context': fields.Raw,
        'opinions': fields.Raw,
        'object_id': fields.String,
        'user_id': fields.String,
        'when': rfields.DateTimestamp,
    }

    def __init__(self, namespace, obj_id, user_id):
        self.namespace = namespace
        self.user = UserModel(namespace, user_id)
        self.obj = ObjModel(namespace, obj_id)
        self.opinion_manager = ObjModel('{0}:{1}'.format(namespace, obj_id), user_id)
        self.hcontext = '{prefix}:obj:{obj_id}:user:{user_id}:hcontext'.format(
            prefix=namespace,
            obj_id=obj_id,
            user_id=user_id
        )

    def set(self, vote, timestamp=None, **kwargs):
        timestamp = timestamp or time.time()
        self.obj.set(self.user, vote, timestamp)
        rclient.delete(self.hcontext)
        if kwargs:
            rclient.hmset(self.hcontext, kwargs)

    def get(self):
        timestamp = self.timestamp
        if not timestamp:
            raise DoesNotExists()
        return {
            'object_id': self.obj.identifier,
            'user_id': self.user.identifier,
            'vote': self.vote,
            'when': self.timestamp,
            'context': self.context,
            'opinions': self.opinion_manager.votemap,
        }

    def delete(self, timestamp=None):
        timestamp = timestamp or time.time()
        self.obj.delete(self.user, timestamp)
        rclient.delete(self.hcontext)

    @property
    def vote(self):
        return self.obj.vote(self.user)

    @property
    def timestamp(self):
        return self.obj.timestamp(self.user)

    @property
    def context(self):
        return rclient.hgetall(self.hcontext)
