#!/usr/local/bin/python
#coding: latin-1

from sopel.module import commands
import urllib2, json, re, requests, idna
from urlparse import urlparse, urlunparse
import lxml.html

# Most of this code was ripped from url.py in sopel's source. Don't kill me.

title_tag_data = re.compile('<(/?)title( [^>]+)?>', re.IGNORECASE)
quoted_title = re.compile('[\'"]<title>[\'"]', re.IGNORECASE)
re_dcc = re.compile(r'(?i)dcc\ssend')
# This sets the maximum number of bytes that should be read in order to find
# the title. We don't want it too high, or a link to a big file/stream will
# just keep downloading until there's no more memory. 640k ought to be enough
# for anybody.
max_bytes = 655360

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
                
                req = urllib2.Request('https://www.googleapis.com/urlshortener/v1/url?key={0}'.format(bot.config.google.api_key),'{{"longUrl": "{0}"}}'.format(url), {'Content-Type' : 'application/json'})
                data = urllib2.urlopen(req)
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
    response = requests.get(url, verify=verify, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'})
    try:
        if isinstance(response.text, unicode):
            t = lxml.html.fromstring(response.text.encode('utf-8'))
        else:
            t = lxml.html.fromstring(response.text)
        return t.find(".//title").text.strip()
    except Exception as e:
        print('[googl][title] {}'.format(e))
        return None

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

@commands('shorten', 'tiny')
def url_command(bot, trigger):
    """Shortens URLs using goo.gl"""
    if trigger.group(2):
        title_auto(bot, trigger)
