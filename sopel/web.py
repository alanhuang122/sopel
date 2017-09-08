# coding=utf-8
"""
*Availability: 3+, depreacted in 6.2.0*

The web class contains essential web-related functions for interaction with web
applications or websites in your modules.  It supports HTTP GET, HTTP POST and
HTTP HEAD.
"""
# Copyright © 2008, Sean B. Palmer, inamidst.com
# Copyright © 2009, Michael Yanovich <yanovich.1@osu.edu>
# Copyright © 2012, Dimitri Molenaars, Tyrope.nl.
# Copyright © 2012-2013, Elad Alfassa, <elad@fedoraproject.org>
# Licensed under the Eiffel Forum License 2.

from __future__ import unicode_literals, absolute_import, print_function, division

import re
import sys
import urllib
import requests

from sopel import __version__
from sopel.tools import deprecated

if sys.version_info.major < 3:
    import httplib
    from htmlentitydefs import name2codepoint
    from urlparse import urlparse
    from urlparse import urlunparse
else:
    import http.client as httplib
    from html.entities import name2codepoint
    from urllib.parse import urlparse
    from urllib.parse import urlunparse
    unichr = chr
    unicode = str

try:
    import ssl
    if not hasattr(ssl, 'match_hostname'):
        # Attempt to import ssl_match_hostname from python-backports
        import backports.ssl_match_hostname
        ssl.match_hostname = backports.ssl_match_hostname.match_hostname
        ssl.CertificateError = backports.ssl_match_hostname.CertificateError
    has_ssl = True
except ImportError:
    has_ssl = False

USER_AGENT = 'Sopel/{} (http://sopel.chat)'.format(__version__)
default_headers = {'User-Agent': USER_AGENT}
ca_certs = None  # Will be overriden when config loads. This is for an edge case.


class MockHttpResponse(httplib.HTTPResponse):
    "Mock HTTPResponse with data that comes from requests."
    def __init__(self, response):
        self.headers = response.headers
        self.status = response.status_code
        self.reason = response.reason
        self.close = response.close
        self.read = response.raw.read
        self.url = response.url

    def geturl(self):
        return self.url

r_entity = re.compile(r'&([^;\s]+);')

def entity(match):
    value = match.group(1).lower()
    if value.startswith('#x'):
        return unichr(int(value[2:], 16))
    elif value.startswith('#'):
        return unichr(int(value[1:]))
    elif value in name2codepoint:
        return unichr(name2codepoint[value])
    return '[' + value + ']'


def decode(html):
    return r_entity.sub(entity, html)

        tmp.update(headers)

# Identical to urllib2.quote
def quote(string, safe='/'):
    """Like urllib2.quote but handles unicode properly."""
    if sys.version_info.major < 3:
        if isinstance(string, unicode):
            string = string.encode('utf8')
        string = urllib.quote(string, safe.encode('utf8'))
    else:
        string = urllib.parse.quote(str(string), safe)
    return string


def quote_query(string):
    """Quotes the query parameters."""
    parsed = urlparse(string)
    string = string.replace(parsed.query, quote(parsed.query, "/=&"), 1)
    return string


# Functions for international domain name magic

def urlencode_non_ascii(b):
    regex = '[\x80-\xFF]'
    if sys.version_info.major > 2:
        regex = b'[\x80-\xFF]'
    return re.sub(regex, lambda c: '%%%02x' % ord(c.group(0)), b)


def iri_to_uri(iri):
    parts = urlparse(iri)
    parts_seq = (part.encode('idna') if parti == 1 else urlencode_non_ascii(part.encode('utf-8')) for parti, part in enumerate(parts))
    if sys.version_info.major > 2:
        parts_seq = list(parts_seq)

    parsed = urlunparse(parts_seq)
    if sys.version_info.major > 2:
        return parsed.decode()
    else:
        return parsed


if sys.version_info.major < 3:
    urlencode = urllib.urlencode
else:
    urlencode = urllib.parse.urlencode
"""
web.py - Web Facilities
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2012, Dimitri Molenaars (Tyrope.nl)
Copyright 2012, Elad Alfassa (elad@fedoraproject.org)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)

More info:
 * Willie: https://willie.dftba.net
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import urllib2
from htmlentitydefs import name2codepoint
from sopel.modules import unicode as uc

r_entity = re.compile(r'&([^;\s]+);')


class Grab(urllib.URLopener):
    def __init__(self, *args):
        self.version = 'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0'
        urllib.URLopener.__init__(self, *args)

    def http_error_default(self, url, fp, errcode, errmsg, headers):
        return urllib.addinfourl(fp, [headers, errcode], "http:" + url)
urllib._urlopener = Grab()


def get(uri):
    if not uri.startswith('http'):
        return
    u = urllib.urlopen(uri)
    bytes = u.read()
    u.close()
    return bytes

def head(uri):
    if not uri.startswith('http'):
        return
    u = urllib.urlopen(uri)
    info = u.info()
    u.close()
    return info

def head_info(uri):
    if not uri.startswith('http'):
        return
    output = dict()

    u = urllib.urlopen(uri)
    if hasattr(u, 'geturl'):
        output['geturl'] = u.geturl()
    if hasattr(u, 'code'):
        output['code'] = u.code
    if hasattr(u, 'url'):
        output['url'] = u.url
    if hasattr(u, 'headers'):
        output['headers'] = u.headers
    if hasattr(u, 'info'):
        output['info'] = u.info()

    u.close()
    return output

def post(uri, query):
    if not uri.startswith('http'):
        return
    data = urllib.urlencode(query)
    u = urllib.urlopen(uri, data)
    bytes = u.read()
    u.close()
    return bytes

def entity(match):
    value = match.group(1).lower()
    if value.startswith('#x'):
        return unichr(int(value[2:], 16))
    elif value.startswith('#'):
        return unichr(int(value[1:]))
    elif value in name2codepoint:
        return unichr(name2codepoint[value])
    return '[' + value + ']'


def decode(html):
    return r_entity.sub(entity, html)

def entity_replace(txt):
    return r_entity.sub(ep, txt)

def ep(m):
    entity = m.group()
    if entity.startswith('&#x'):
        cp = int(entity[3:-1], 16)
        meep = unichr(cp)
    elif entity.startswith('&#'):
        cp = int(entity[2:-1])
        meep = unichr(cp)
    else:
        entity_stripped = entity[1:-1]
        try:
            char = name2codepoint[entity_stripped]
            meep = unichr(char)
        except:
            if entity_stripped in HTML_ENTITIES:
                meep = HTML_ENTITIES[entity_stripped]
            else:
                meep = str()
    try:
        return uc.decode(meep)
    except:
        return uc.decode(uc.encode(meep))


def remove_xml_tags(txt):
    r_tag = re.compile(r'<(?!!)[^>]+>')
    return re.sub(r_tag, '', txt)


def get_urllib_object(uri, timeout):
    '''Return a urllib2 object for `uri` and `timeout`. This is better than
    using urrlib2 directly, for it handles redirects, makes sure URI is utf8,
    and is shorter and easier to use.
    Modules may use this if they need a urllib2 object to execute .read() on.
    For more information, refer to the urllib2 documentation.'''
    redirects = 0
    try:
        uri = uri.encode("utf-8")
    except:
        pass
    while True:
        req = urllib2.Request(uri, headers={'Accept': '*/*', 'User-Agent': 'Mozilla/5.0 (Jenni)'})
        try:
            u = urllib2.urlopen(req, None, timeout)
        except urllib2.HTTPError, e:
            return e.fp
        except:
            raise
        info = u.info()
        if not isinstance(info, list):
            status = '200'
        else:
            status = str(info[1])
            try: info = info[0]
            except: pass
        if status.startswith('3'):
            uri = urlparse.urljoin(uri, info['Location'])
        else: break
        redirects += 1
        if redirects >= 50:
            return "Too many re-directs."
    return u

def urlencode(data):
    '''Identical to urllib.urlencode. Use this if you already importing web
    in your module and don't want to import urllib just to use the urlencode
    function.'''
    return urllib.urlencode(data)


if __name__ == "__main__":
    main()
