#!/usr/bin/env python

import os
import sys

import mandrill
import pystache

from lib import db
from lib import log


template = """Hi!

These {{count}} URLs were shared at least {{threshold}} times by the accounts
you follow on Twitter. I hope you find something cool or interesting!

{{#links}}
    {{url}}{{#sources}}
      - {{url}}{{/sources}}

{{/links}}
Have fun,


Your very own Thresholderbot
"""


def send_mail(records, threshold, dry_run):
    ctx = {
        'count': len(records),
        'threshold': threshold,
        'links': [{
            'url': rec['url'],
            'sources': [{ 'url': src } for src in rec['source_urls']],
        } for rec in records],
    }
    body = pystache.render(template, ctx)

    if dry_run:
        print body
        return False

    m = mandrill.Mandrill(os.environ['MANDRILL_APIKEY'])
    resp = m.messages.send({
        'from_email': os.environ['FROM_ADDRESS'],
        'to': [{'email': os.environ['TO_ADDRESS']}],
        'subject': 'New links from your Thresholderbot',
        'text': body,
    })
    if resp[0]['status'] != 'sent':
        log.error('Error sending mail: %r', resp)
        return False
    return True


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
