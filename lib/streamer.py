"""
An attempt at a simple interface for consuming a Twitter stream.
"""

import contextlib
import json
import os
import urllib2

from oauth import oauth

from lib import log


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
    log.debug('Connecting to %s', url)
    try:
        handle = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        log.error('Error connecting to %s', url)
        log.error('%s %s', e.code, e.reason)
        log.error('Body: %r', e.read())
        raise
    else:
        yield handle
        log.info('Closing connection...')
        handle.close()


def process_stream(stream):
    while True:
        length_bytes = stream.readline().strip()
        if not length_bytes.isdigit():
            continue
        message_bytes = stream.read(int(length_bytes))
        try:
            message = json.loads(message_bytes)
        except json.JSONDecodeError, e:
            log.error('Invalid JSON: %s: %r', e, message_bytes)
        else:
            yield message


def iter_stream(stream_url, params=None):
    with open_stream(stream_url, params) as stream:
        for message in process_stream(stream):
            yield message
