import cgi
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
        #  1. http://flic.kr/p/ekDbXt
        #  2. http://www.flickr.com/photo.gne?short=ekDbXt
        #  3. /photos/raganwald/8754907409/
        # So let's make sure we're always returning a full URL.
        if next.startswith('/'):
            scheme, netloc, _, _, _ = urlparse.urlsplit(url)
            next = scheme + '://' + netloc + next
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
