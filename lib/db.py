"""
Records are stored in mongodb in the following format:

    {
        'url': <url>,
        'src': <source_url>,
        'seen': <0 or 1>,
    }

This module provides a dead-simple interface for inserting/updating records
and for fetching records over a certain threshold.
"""

import os
import urlparse

import pymongo
from lib import log


def add(url, source_url):
    """Add a URL to the datastore."""
    return DB.urls.insert({
        'url': url,
        'src': source_url,
        'seen': 0,
    })


def mark_seen(url):
    """Mark any records matching the given URL as seen."""
    query = {
        'url': url,
        'seen': 0,
    }
    update = {
        '$set': { 'seen': 1, },
    }
    return DB.urls.update(query, update, multi=True)


def aggregate(threshold):
    """Fetch a collection of records containing all URLs appearing more than
    threshold times.
    """
    assert isinstance(threshold, int)

    results = DB.urls.aggregate([
        # only match unseen documents
        { '$match': { 'seen': 0 } },
        # group by URL, aggregating source URLs and counting occurrences
        {
            '$group': {
                '_id': '$url',
                'source_urls': {
                    '$push': '$src',
                },
                'count': {
                    '$sum': 1
                },
            },
        },
        # only include aggregated docs with a count over the given threshold
        { '$match': { 'count': { '$gte': threshold } } },
        # sort by how many occurrences there were
        { '$sort': { 'count': -1 } },
    ])

    # Reshape the data for our uses
    return [{
        'url': rec['_id'],
        'count': rec['count'],
        'source_urls': rec['source_urls']
    } for rec in results['result']]


class DB(object):
    """A proxy wrapper around a mongodb that connects on demand."""

    _db = None

    def _connect(self):
        if self._db is None:
            mongo_url = os.environ.get('MONGOHQ_URL')
            if mongo_url:
                log.info('Connecting to mongodb: %s', mongo_url)
                conn = pymongo.MongoClient(mongo_url)
                db = conn[urlparse.urlparse(mongo_url).path[1:]]
            else:
                log.info('Connecting to local mongodb...')
                conn = pymongo.MongoClient()
                db = conn['thresholder']

            if 'urls' not in db.collection_names():
                db.create_collection('urls')

            self._db = db
        return self._db

    def __getattr__(self, name):
        self._connect()
        return getattr(self._db, name)

DB = DB()
