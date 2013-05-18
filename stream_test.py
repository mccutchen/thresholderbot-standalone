import logging
import sys

import requests

import db
import streamer
import urlwork


STREAM_URL = "https://userstream.twitter.com/2/user.json"


def handle_message(message):
    if 'text' in message:
        if message['entities']:
            for url_info in message['entities']['urls']:
                url = url_info['expanded_url']
                logging.info('Found URL: %s', url)
                try:
                    canonical_url = urlwork.canonicalize(url)
                except requests.TooManyRedirects:
                    logging.error('Too many redirects: %s', url)
                except Exception, e:
                    logging.exception('Uncaught exception: %s', e)
                    logging.error('url info: %r', url_info)
                else:
                    if canonical_url != url:
                        logging.info(' => %s', canonical_url)
                    source_url = 'https://twitter.com/%s/status/%s' % (
                        message['user']['screen_name'], message['id'])
                    db.add(canonical_url, source_url)
    else:
        logging.warn('Skipping message: %r', message)


def main():
    params = {
        'replies': 'all',
    }
    try:
        for i, message in enumerate(streamer.iter_stream(STREAM_URL, params)):
            handle_message(message)
            if i and i % 20 == 0:
                logging.info('Processed %d messages', i)
    except KeyboardInterrupt:
        logging.info('Bye bye!')
    except Exception, e:
        logging.exception('Uncaught exception: %s', e)
        return 1
    return 0


if __name__ == '__main__':
    logging.getLogger().setLevel(level=logging.INFO)
    sys.exit(main())
