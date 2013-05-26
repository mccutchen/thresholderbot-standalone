import hashlib
import os
import time

import redis
from lib import log


def sha1_hash(s):
    return hashlib.sha1(s).hexdigest()


def add(url, source_id, source_url):
    """Add a URL from a specific source to the datastore. source_id should be
    the Twitter user ID of a source and source_url should be the URL to the
    specific tweet where the URL was found.

    Returns the number of times we've seen the URL.

    Under the hood, information about a URL is recorded in a couple of places:

     1. The source_url is stored under a key composed of the sha1 hashes of
        the source_id and the url. This ensures that we record only the first
        source of a given URL shared by a given user.

     2. The key from above is added to a set under a key composed of the sha1
        hash of the url. The size of this set indicates whether a given link
        is over the threshold. The sort value of the key in the set is the
        timestamp at which we saw the corresponding URL.
    """
    url_hash = sha1_hash(url)
    source_hash = sha1_hash(str(source_id))

    url_key = 'url:' + url_hash
    source_key = 'src:{}:{}'.format(source_hash, url_hash)
    ttl = 60 * 60 * 12

    pipe = DB.pipeline()
    pipe.setnx(source_key, source_url)
    pipe.zadd(url_key, source_key, time.time())
    pipe.zcount(url_key, '-inf', 'inf')
    pipe.expire(url_key, ttl)
    source_key_added, url_key_added, url_key_count, _ = pipe.execute()

    if bool(source_key_added) != bool(url_key_added):
        log.warn('Inconsistent state: %s=%r, %s=%r',
                 source_key, source_key_added, url_key, url_key_added)

    if not url_key_added:
        log.info('URL %s from user %s already in datastore', url, source_id)

    return url_key_count


def is_seen(url):
    """Returns a bool indicating whether a notification for the url has been
    sent out.
    """
    return DB.get('seen:' + sha1_hash(url)) is not None


def mark_seen(url):
    """Add a tombstone key for the url to indicate that a notification has
    been sent.
    """
    return DB.set('seen:' + sha1_hash(url), 1)


def get_source_urls(url):
    """Return a list of (source url, timestamp) tuples for each source of the
    given URL.
    """
    url_key = 'url:' + sha1_hash(url)
    sources = DB.zrange(url_key, 0, -1, withscores=1)
    source_keys = [key for key, _ in sources]
    source_timestamps = [value for _, value in sources]
    source_urls = DB.mget(*source_keys)
    return [(src, ts) for src, ts in zip(source_urls, source_timestamps)]


class DB(object):
    """A proxy wrapper around a redis db that connects on demand."""

    _redis = None

    def _connect(self):
        if self._redis is None:
            redis_url = os.getenv('REDISCLOUD_URL', 'redis://localhost:6379')
            log.info('Connecting to redis: %s', redis_url)
            self._redis = redis.from_url(redis_url)
        return self._redis

    def __getattr__(self, name):
        self._connect()
        return getattr(self._redis, name)

DB = DB()
