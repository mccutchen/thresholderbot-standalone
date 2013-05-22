"""
An attempt at a simple interface for consuming a Twitter stream.
"""

import json
import os
import requests

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

    return oauth_request.to_url()


def iter_stream(stream_url, params=None):
    url = prepare_request(stream_url, params)
    log.debug('Connecting to %s', url)
    resp = requests.get(url, stream=True)
    for line in resp.iter_lines():
        if line.strip():
            try:
                message = json.loads(line)
            except json.JSONDecodeError, e:
                log.error('Invalid JSON: %s: %r', e, line)
            else:
                yield message
