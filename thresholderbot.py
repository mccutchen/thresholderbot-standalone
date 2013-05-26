#!/usr/bin/env python

import os
import sys

import requests

from lib import db
from lib import log
from lib import notifications
from lib import streamer
from lib import urlwork


STREAM_URL = "https://userstream.twitter.com/2/user.json"


def handle_message(message):
    if 'text' in message and message['entities']:
        return handle_message_with_entities(message)
    elif 'friends' in message:
        log.info('Got %d friends on startup', len(message['friends']))
    elif 'delete' in message:
        pass
    else:
        log.warn('Skipping message: %r', message)


def handle_message_with_entities(message):
    assert message['entities']
    for url_info in message['entities']['urls']:
        url = url_info['expanded_url']
        log.info('Found URL: %s', url)
        try:
            canonical_url = urlwork.canonicalize(url)
        except requests.TooManyRedirects:
            log.error('Too many redirects: %s', url)
        except Exception, e:
            log.exception('Canonicalization error: %s', e)
            log.error('URL info: %r', url_info)
        else:
            if canonical_url != url:
                log.info('=> %s', canonical_url)

            source = message['user']['id']
            source_url = make_tweet_url(message)
            count = db.add(canonical_url, source, source_url)

            if count >= int(os.environ.get('THRESHOLD', 5)):
                log.info('URL %s seen %d times!', canonical_url, count)
                handle_thresholded_url(canonical_url)


def handle_thresholded_url(url):
    if not db.was_sent(url):
        sources = db.get_source_urls(url)
        if notifications.send_mail(url, sources):
            db.mark_sent(url)
    else:
        log.warn('Skipping already-seen URL %s', url)


def make_tweet_url(message):
    return 'https://twitter.com/%s/status/%s' % (
        message['user']['screen_name'],
        message['id'])


def main():
    try:
        for i, message in enumerate(streamer.iter_stream(STREAM_URL)):
            handle_message(message)
            if i and i % 100 == 0:
                log.info('Processed %d messages', i)
    except KeyboardInterrupt:
        log.info('Bye bye!')
    except Exception, e:
        log.exception('Error handling message: %s', e)
        log.warn('Exiting...')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
