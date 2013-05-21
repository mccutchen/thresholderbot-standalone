import logging
import sys

import requests

from lib import db
from lib import streamer
from lib import urlwork


STREAM_URL = "https://userstream.twitter.com/2/user.json"


def handle_message(message):
    if 'text' in message and message['entities']:
        return handle_message_with_entities(message)
    elif 'friends' in message:
        logging.info('Got %d friends on startup', len(message['friends']))
    elif 'delete' in message:
        pass
    else:
        logging.warn('Skipping message: %r', message)


def handle_message_with_entities(message):
    assert message['entities']
    for url_info in message['entities']['urls']:
        url = url_info['expanded_url']
        logging.info('Found URL: %s', url)
        try:
            canonical_url = urlwork.canonicalize(url)
        except requests.TooManyRedirects:
            logging.error('Too many redirects: %s', url)
        except Exception, e:
            logging.exception('Canonicalization error: %s', e)
            logging.error('URL info: %r', url_info)
        else:
            if canonical_url != url:
                logging.info(' => %s', canonical_url)
            db.add(canonical_url, make_tweet_url(message))


def make_tweet_url(message):
    return 'https://twitter.com/%s/status/%s' % (
        message['user']['screen_name'],
        message['id'])


def main():
    params = {}
    try:
        for i, message in enumerate(streamer.iter_stream(STREAM_URL, params)):
            handle_message(message)
            if i and i % 20 == 0:
                logging.info('Processed %d messages', i)
    except KeyboardInterrupt:
        logging.info('Bye bye!')
    except Exception, e:
        logging.exception('Error handling message: %s', e)
        logging.warn('Exiting...')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
