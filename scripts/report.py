#!/usr/bin/env python

import os
import sys

import pystache
import requests

from lib import db
from lib import log


template = """Hi!

These {{count}} URLs were shared at least {{threshold}} times in the past
{{window}}. I hope you find something cool or interesting!

{{#links}}
    {{url}}{{#sources}}
      - {{url}}{{/sources}}

{{/links}}
Have fun,


Your friendly neighborhood Twitter Link Robot Thingy
"""


def send_mail(records, threshold, dry_run):
    ctx = {
        'count': len(records),
        'window': 'hour',
        'threshold': threshold,
        'links': [{
            'url': rec['url'],
            'sources': [{ 'url': src } for src in rec['source_urls']],
        } for rec in records],
    }
    body = pystache.render(template, ctx)

    api_key = os.environ['MAILGUN_API_KEY']
    mailgun_domain = os.environ['MAILGUN_DOMAIN']
    api_url = 'https://api:{}@api.mailgun.net/v2/{}'.format(
        api_key, mailgun_domain)

    params = {
        'from': 'thresholder@{}'.format(mailgun_domain),
        'to': os.environ['TO_ADDRESS'],
        'subject': 'Links from your Twitter Thresholder',
        'text': body,
    }

    if dry_run:
        print body
        return False

    resp = requests.post(api_url + '/messages', data=params)
    if resp.status_code >= 400:
        log.error(
            'Error sending mail: HTTP %d: %r', resp.status_code, resp.json())
    return 200 <= resp.status_code < 400


def main(dry_run):
    threshold = int(os.environ.get('THRESHOLD', 5))
    records = db.aggregate(threshold)
    log.info('Found %d links > threshold %d', len(records), threshold)
    if records and send_mail(records, threshold, dry_run):
        for rec in records:
            continue
            db.mark_seen(rec['url'])
    return 0


if __name__ == '__main__':
    dry_run = len(sys.argv) > 1 and sys.argv[1] == '--dry-run'
    sys.exit(main(dry_run))
