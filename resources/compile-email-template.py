#!/usr/bin/env python

import os
import sys

import requests

from lib import log


def main():
    template_name = 'email.html.mustache'
    template_path = os.path.join(os.path.dirname(__file__), template_name)

    url = 'http://premailer.dialect.ca/api/0.1/documents'
    data = {
        'html': open(template_path).read(),
        'preserve_styles': 'false',
    }
    resp = requests.post(url, data=data)
    if resp.status_code != 201 or 'Location' not in resp.headers:
        log.error('Error: HTTP %s: %s', resp.status_code, resp.content)
        return 1
    compiled = requests.get(resp.headers['Location']).content
    # Sometimes the compiler mangles the template syntax, such that
    #
    #   <a href="{{url}}">
    #
    # becomes
    #
    #   <a href="%7B%7Burl%7D%7D">
    print compiled.replace('%7B%7B', '{{').replace('%7D%7D', '}}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
