import cgi
import logging
import re
import urllib
import urlparse

import requests
import urlnorm


def canonicalize(url):
    """Canonicalize a URL in just a few easy steps:

        1. Resolve any redirects
        2. Normalize the URL
        3. Strip any superflous query params
        4. Sort any remaining query params
        5. Profit!

    This relies on the urlnorm module for normalization, and, at the moment,
    just removes utm_* query params.

    TODO: Special case normalization for major sites (e.g. youtube)?
    """
    url = urlnorm.norm(resolve(url))
    url_parts = urlparse.urlsplit(url)
    scheme, netloc, path, query, fragment = url_parts

    params = []
    for key, value in cgi.parse_qs(query).iteritems():
        if exclude_param(url_parts, key, value):
            continue
        if isinstance(value, list):
            params.extend((key, v) for v in value)
        else:
            params.append((key, value))

    query = urllib.urlencode(sorted(params), doseq=1)
    return urlparse.urlunsplit((scheme, netloc, path, query, ''))


def exclude_param(url_parts, key, value):
    """Returns True if the given query parameter should be excluded from the
    canonicalized version of a URL.
    """
    if url_parts.netloc.endswith('youtube.com'):
        return key not in ('v', 'p')
    return key.startswith('utm_')


def resolve(url, depth=0):
    """Resolve any redirects and return the final URL."""
    if depth > 10:
        raise requests.TooManyRedirects()
    resp = requests.head(url)
    next = resp.headers.get('Location')
    if next and next != url:
        # Flickr (and maybe other) URLs end up resolving to a relative path:
        #
        #  1. http://flic.kr/p/ekDbXt
        #  2. http://www.flickr.com/photo.gne?short=ekDbXt
        #  3. /photos/raganwald/8754907409/
        #
        # So let's make sure we're always returning a full URL.
        if next.startswith('/'):
            logging.debug('Relative redirect: %r => %r', url, next)
            scheme, netloc, _, _, _ = urlparse.urlsplit(url)
            next = scheme + '://' + netloc + next

        # Special case for nytimes paywall infinite redirects:
        #
        #  1. http://www.nytimes.com/2013/05/20/sports/basketball/for-knicks-already-out-of-playoffs-magic-may-run-out.html?smid=tw-share&_r=0
        #  2. http://www.nytimes.com/glogin?URI=http://www.nytimes.com/2013/05/20/sports/basketball/for-knicks-already-out-of-playoffs-magic-may-run-out.html&OQ=smidQ3Dtw-shareQ26_rQ3D1Q26&OP=ca2ca394Q2FJQ3FQ60Q3CJv9Q3CJnnnJQ51Q3CQ7DDJcQ3FaQ7ChQ3FQ3FQ3CQ2BJQ2B@fQ25J@dJQ2B@JQ7CQ60Q3FhQ3CQ7CJ7_Q7CjiQ3C7_DDJNQ3Fh!jvQ3EajQ7C!_Dhi_c9!Q3FqQ3C!Q3FN!Q60D_9Q3FNNQ7C!Q7D_1Q3Ea!Q7D_9!hqv!Q3FqQ3CuQ51Q3CQ7DD
        #  3. GOTO 1
        #
        # So if we get to the /glogin location, just pull the final URL out of
        # its query params.
        if re.match('^https?://(www\.)?nytimes\.com/glogin', next):
            scheme, netloc, path, query, fragment = urlparse.urlsplit(next)
            params = cgi.parse_qs(query)
            if 'URI' in params:
                final_url = params['URI'][0]
                logging.debug('nytimes paywall: %r => %r', next, final_url)
                return final_url

        logging.debug('Redirect %d: %r => %r', depth, url, next)
        return resolve(next, depth + 1)
    else:
        return url


if __name__ == '__main__':
    import fileinput
    for line in fileinput.input():
        url = line.strip()
        try:
            print canonicalize(url)
        except requests.TooManyRedirects:
            print 'TOO MANY REDIRECTS: %s' % url
