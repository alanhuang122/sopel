#!/usr/local/bin/python
#coding: latin-1

from sopel import web
from sopel.module import commands
import urllib2, json, re, requests

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
                url = web.iri_to_uri(url)
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
    """Return the title for the given URL."""
    response = requests.get(url, stream=True, verify=verify, headers={'User-Agent':'Sopel'})
    try:
        content = ''
        for byte in response.iter_content(chunk_size=512, decode_unicode=True):
            if not isinstance(byte, bytes):
                content += byte
            else:
                break
            if '</title>' in content or len(content) > max_bytes:
                break
    except UnicodeDecodeError:
        return  # Fail silently when data can't be decoded
    finally:
        # need to close the connexion because we have not read all the data
        response.close()

    # Some cleanup that I don't really grok, but was in the original, so
    # we'll keep it (with the compiled regexes made global) for now.
    content = title_tag_data.sub(r'<\1title>', content)
    content = quoted_title.sub('', content)

    start = content.find('<title>')
    end = content.find('</title>')
    if start == -1 or end == -1:
        return
    title = web.decode(content[start + 7:end])
    title = title.strip()[:200]

    title = ' '.join(title.split())  # cleanly remove multiple spaces

    # More cryptic regex substitutions. This one looks to be myano's invention.
    title = re_dcc.sub('', title)

    return title or None

@commands('shorten', 'tiny')
def url_command(bot, trigger):
    """Shortens URLs using goo.gl"""
    if trigger.group(2):
        title_auto(bot, trigger)
