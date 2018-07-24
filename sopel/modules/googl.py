#!/usr/local/bin/python
#coding: latin-1

from sopel.module import commands
import urllib.request, urllib.error, urllib.parse, json, re, requests, idna
from urllib.parse import urlparse, urlunparse
import lxml.html
from ftfy import fix_encoding

# Most of this code was ripped from url.py in sopel's source. Don't kill me.

title_tag_data = re.compile('<(/?)title( [^>]+)?>', re.IGNORECASE)
quoted_title = re.compile('[\'"]<title>[\'"]', re.IGNORECASE)
re_dcc = re.compile(r'(?i)dcc\ssend')
# This sets the maximum number of bytes that should be read in order to find
# the title. We don't want it too high, or a link to a big file/stream will
# just keep downloading until there's no more memory. 640k ought to be enough
# for anybody.
max_bytes = 655360
user_agent = None

def setup(bot):
    global user_agent
    user_agent = bot.config.url.user_agent

def title_auto(bot, trigger):
    """
    Automatically show titles for URLs. For shortened URLs/redirects, find
    where the URL redirects to and show the title for that (or call a function
    from another module to give more information).
    """
    # Avoid fetching known malicious links
    if 'safety_cache' in bot.memory and trigger in bot.memory['safety_cache']:
        if bot.memory['safety_cache'][trigger]['positives'] > 1:
            return
    url_finder = re.compile(r'(?u)(%s?(?:http|https|ftp)(?:://\S+))' %
                            (bot.config.url.exclusion_char), re.IGNORECASE)
    urls = re.findall(url_finder, trigger)
    if len(urls) == 0:
        bot.say("Couldn't find URLs.")
        return

    results = process_urls(bot, trigger, urls)
    bot.memory['last_seen_url'][trigger.sender] = urls[-1]

    for title, domain in results[:4]:
        message = '%s - [ %s ]' % (domain, title)
        # Guard against responding to other instances of this bot.
        if message != trigger:
            bot.say(message)


def process_urls(bot, trigger, urls):
    """
    For each URL in the list, ensure that it isn't handled by another module.
    If not, find where it redirects to, if anywhere. If that redirected URL
    should be handled by another module, dispatch the callback for it.
    Return a list of (title, hostname) tuples for each URL which is not handled by
    another module.
    """

    results = []
    for url in urls:
        if not url.startswith(bot.config.url.exclusion_char):
            # Magic stuff to account for international domain names
            try:
                parts = urlparse(url)
                parts._replace(netloc=idna.encode(parts.netloc))
                url = urlunparse(parts)
            except:
                pass
            title = find_title(url, verify=bot.config.core.verify_ssl)
            if title:
                
                req = urllib.request.Request('https://www.googleapis.com/urlshortener/v1/url?key={0}'.format(bot.config.google.api_key),'{{"longUrl": "{0}"}}'.format(url).encode('utf-8'), {'Content-Type' : 'application/json'})
                data = urllib.request.urlopen(req)
                response = json.load(data)
                if 'error' in response:
                    bot.say(response['message'])
                    return
                thisurl = response['id']
                results.append((title, thisurl))
            else:
                bot.say("URL not found")
    return results

def find_title(url, verify=True):
    """Return the title for the given URL."""
    try:
        response = requests.get(url, verify=verify, headers={'User-Agent': user_agent, 'Accept': 'text/html'})
    except requests.exceptions.ConnectionError as e:
        if '[Errno -2]' in str(e):  #name or service not known
            print(('[url] name or service not known: {}'.format(url)))
            return None
        if '[Errno 111]' in str(e): #connection refused
            print(('[url] connection refused: {}'.format(url)))
            return None
        raise e
    except requests.exceptions.ReadTimeout:
        print(('[url] connection timed out: {}'.format(url)))
        return None
    if 'text/plain' in response.headers['Content-Type']:
        print(('Content-Type for url {} is text/plain; skipping'.format(url)))
        return None
    try:
        t = lxml.html.fromstring(fix_encoding(response.text))
        return t.find(".//title").text.strip()
    except Exception as e:
        print(('exception on url {}'.format(url)))
        print(('[url] {}'.format(e)))
        return None

r_entity = re.compile(r'&([^;\s]+);')

def entity(match):
    value = match.group(1).lower()
    if value.startswith('#x'):
        return chr(int(value[2:], 16))
    elif value.startswith('#'):
        return chr(int(value[1:]))
    elif value in name2codepoint:
        return chr(name2codepoint[value])
    return '[' + value + ']'

def decode(html):
    return r_entity.sub(entity, html)

#@commands('shorten', 'tiny')
def url_command(bot, trigger):
    """Shortens URLs using goo.gl"""
    if trigger.group(2):
        title_auto(bot, trigger)
