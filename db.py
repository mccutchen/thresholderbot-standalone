"""
Records are stored in mongodb in the following format:

    {
        'url': <url>,
        'source': <source_url>,
    }

This module provides a dead-simple interface for inserting/updating records
and for fetching records over a certain threshold.
"""

import logging
import os
import urlparse

import pymongo


def add(url, source_url):
    """Add a URL to the datastore."""
    return DB.thresholder.insert({
        'url': url,
        'src': source_url,
    })


def remove(url):
    """Remove any records matching the given URL from the datastore."""
    return DB.thresholder.remove({
        'url': url,
    })


def aggregate(threshold):
    """Fetch a collection of records containing all URLs appearing more than
    threshold times.
    """
    assert isinstance(threshold, int)
    pass


class DB(object):
    """A proxy wrapper around a mongodb that connects on demand."""

    _db = None

    def _connect(self):
        if self._db is None:
            mongo_url = os.environ.get('MONGOHQ_URL')
            if mongo_url:
                logging.info('Connecting to mongodb: %s', mongo_url)
                conn = pymongo.MongoClient(mongo_url)
                db = conn[urlparse.urlparse(mongo_url).path[1:]]
            else:
                logging.info('Connectiong to local mongodb')
                conn = pymongo.MongoClient()
                db = conn['thresholder']
            # Ensure our 10mb capped collection is in place
            db.create_collection('thresholder', capped=True, size=10485760)
            self._db = db
        return self._db

    def __getattr__(self, name):
        self._connect()
        return getattr(self._db, name)

DB = DB()
