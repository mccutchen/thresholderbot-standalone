import logging
import sys

import streamer


STREAM_URL = "https://userstream.twitter.com/2/user.json"


def handle_message(message):
    if 'text' in message:
        if message['entities']:
            for url_info in message['entities']['urls']:
                url = url_info['expanded_url']
                logging.info('Found URL: %s', url)
                print ' '.join((
                    message['user']['screen_name'],
                    str(message['user']['id']),
                    url))
                sys.stdout.flush()
    else:
        logging.debug('Skipping message: %r', message)


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
    logging.getLogger().setLevel(level=logging.DEBUG)
    sys.exit(main())
