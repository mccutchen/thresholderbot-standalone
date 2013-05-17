"""
An attempt at a simple interface for consuming a Twitter stream.
"""

import contextlib
import json
import logging
import os
import urllib2

from oauth import oauth


def prepare_request(stream_url, params):
    consumer_token = oauth.OAuthToken(
        os.environ['CONSUMER_KEY'],
        os.environ['CONSUMER_SECRET'])

    access_token = oauth.OAuthToken(
        os.environ['ACCESS_TOKEN_KEY'],
        os.environ['ACCESS_TOKEN_SECRET'])

    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer_token,
        access_token,
        http_method='GET',
        http_url=stream_url,
        parameters=params)

    oauth_request.sign_request(
        oauth.OAuthSignatureMethod_HMAC_SHA1(),
        consumer_token,
        access_token)

    return oauth_request


@contextlib.contextmanager
def open_stream(stream_url, params=None):
    default_params = {
        'delimited': 'length',
    }
    default_params.update(params or {})
    oauth_request = prepare_request(stream_url, default_params)
    url = oauth_request.to_url()
    logging.debug('Connecting to %s', url)
    handle = urllib2.urlopen(url)
    yield handle
    logging.debug('Closing connection...')
    handle.close()


def process_stream(stream):
    while True:
        length = int(stream.readline())
        message_bytes = stream.read(length)
        try:
            message = json.loads(message_bytes)
        except json.JSONDecodeError, e:
            logging.error('Invalid JSON: %s: %r', e, message_bytes)
        else:
            yield message


def iter_stream(stream_url, params=None):
    with open_stream(stream_url, params) as stream:
        for message in process_stream(stream):
            yield message
