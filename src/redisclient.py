# -*- coding: utf-8 -*-
import redis

__all__ = ["RedisClient"]


class RedisClient:
    def __init__(self):
        self.conn = redis.StrictRedis(host='xxx.xxx.xxx.xxx', port=6379, db=1, password='xxx', encoding='utf-8')

    def set(self, key, val):
        try:
            ret = self.conn.set(key, val)
            return ret
        except Exception, exception:
            raise exception

    def exists(self, key):
        try:
            ret = self.conn.exists(key)
            return ret
        except Exception, exception:
            raise exception

    def get_by_key(self, key):
        try:
            value = self.conn.get(key)
            return value
        except Exception, exception:
            raise exception

    def get_by_keys(self, keylist):
        try:
            value_list = self.conn.mget(keylist)
            key_value_dict = {}
            for i in range(len(keylist)):
                key_value_dict[keylist[i]] = value_list[i]
            return key_value_dict
        except Exception, exception:
            raise exception

    def set_by_dict(self, key_value_dict):
        try:
            self.conn.mset(key_value_dict)
        except Exception, exception:
            raise exception

    def set_ex_by_key(self, key, val, kepp_time):
        try:
            ret = self.conn.setex(key, kepp_time, val)
            return ret
        except Exception, exception:
            raise exception

    def del_by_key(self, key):
        try:
            self.conn.delete(key)
        except Exception, exception:
            raise exception

    def hmget_by_keys(self, name, keylist):
        try:
            value_list = self.conn.hmget(name, keylist)
            key_value_dict = {}
            for i in range(len(value_list)):
                key_value_dict[keylist[i]] = value_list[i]
            return key_value_dict
        except Exception, exception:
            raise exception
