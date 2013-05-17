import logging
import sys

import streamer


STREAM_URL = "https://userstream.twitter.com/2/user.json"


TWEET_COUNT = 0
LINK_COUNT = 0
OTHER_COUNT = 0


def handle_message(message):
    global TWEET_COUNT, LINK_COUNT, OTHER_COUNT
    if 'text' in message:
        TWEET_COUNT += 1
        if message['entities']:
            logging.info('Found entities: %r', message['entities'])
            LINK_COUNT += 1
    else:
        OTHER_COUNT += 1
        logging.debug('Skipping message: %r', message)
    return True


def main():
    params = {
        'replies': 'all',
    }
    for i, message in enumerate(streamer.iter_stream(STREAM_URL, params)):
        handle_message(message)
        if i % 50 == 0:
            logging.info('Processed %d messages', i)
            logging.info(
                'Counts: %05d/%05d/%05d',
                TWEET_COUNT, LINK_COUNT, OTHER_COUNT)
    return 0


if __name__ == '__main__':
    logging.getLogger().setLevel(level=logging.DEBUG)
    sys.exit(main())
