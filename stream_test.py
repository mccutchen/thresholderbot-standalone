import json
import logging
import os
import sys
import urllib2

from oauth import oauth


STREAM_URL = "https://userstream.twitter.com/2/user.json"


def open_stream(params=None):
    params = params or {}

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
        http_url=STREAM_URL,
        parameters=params)

    oauth_request.sign_request(
        oauth.OAuthSignatureMethod_HMAC_SHA1(),
        consumer_token,
        access_token)

    url = oauth_request.to_url()
    logging.debug('Connecting to %s', url)
    return urllib2.urlopen(url)


def process_stream(stream, message_callback):
    while True:
        length = int(stream.readline())
        message_bytes = stream.read(length)
        try:
            message = json.loads(message_bytes)
        except json.JSONDecodeError, e:
            logging.error('Invalid JSON: %s: %r', e, message_bytes)
        else:
            message_callback(message)


def handle_message(message):
    if 'text' in message and 'user' in message:
        screen_name = message['user']['screen_name']
        user_id = message['user']['id']
        text = message['text']
        print '@%s (%s): %s' % (screen_name, user_id, text)
        print
    else:
        logging.debug('Skipping message: %r', message)
    return True


def main():
    stream = open_stream({
        'delimited': 'length',
        'replies': 'all',
    })
    try:
        process_stream(stream, handle_message)
    except KeyboardInterrupt:
        logging.info('Exiting...')
    except Exception, e:
        logging.exception('Uncaught exception: %s', e)
        return 1
    return 0


if __name__ == '__main__':
    logging.getLogger().setLevel(level=logging.DEBUG)
    sys.exit(main())
