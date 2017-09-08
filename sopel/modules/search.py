# coding=utf-8
# Copyright 2008-9, Sean B. Palmer, inamidst.com
# Copyright 2012, Elsie Powell, embolalia.com
# Licensed under the Eiffel Forum License 2.
from __future__ import unicode_literals, absolute_import, print_function, division

import re
import requests
from sopel import web
from sopel.module import commands, example
from sopel.trigger import PreTrigger
import json
import sys

from sopel.modules.url import find_title

if sys.version_info.major < 3:
    from urllib import quote_plus
else:
    from urllib.parse import quote_plus

def google(query, key):
    url = 'https://www.googleapis.com/customsearch/v1'
    data = requests.get(url, params={'key' : key, 'cx': '005137987755203522487:jb4yson7hu0', 'q' : query}).json()
    if 'items' not in data:
        return None
    results = data['items']
    return web.decode(results[0]['link'])

r_duck = re.compile(r'nofollow" class="[^"]+" href="(?!https?:\/\/r\.search\.yahoo)(.*?)">')

def duck_search(query):
    query = query.replace('!', '')
    uri = 'http://duckduckgo.com/html/?q=%s&kl=uk-en' % query
    bytes = requests.get(uri, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}).text
    if 'web-result' in bytes:  # filter out the adds on top of the page
        bytes = bytes.split('web-result')[1]
    m = r_duck.search(bytes)
    if m:
        return web.decode(m.group(1))

def duck_api(query):
    if '!bang' in query.lower():
        return 'https://duckduckgo.com/bang.html'

    # This fixes issue #885 (https://github.com/sopel-irc/sopel/issues/885)
    # It seems that duckduckgo api redirects to its Instant answer API html page
    # if the query constains special charactares that aren't urlencoded.
    # So in order to always get a JSON response back the query is urlencoded
    query = quote_plus(query)
    uri = 'http://api.duckduckgo.com/?q=%s&format=json&no_html=1&no_redirect=1' % query
    response = requests.get(uri, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'})
    results = json.loads(response.text)
    if results['Redirect']:
        return results['Redirect']
    else:
        return None

@commands('g','search')
def gs(bot, trigger):
    query = trigger.group(2)
    if not query:
        return bot.reply('What do you want me to search for?')
    result = google(query, bot.config.google.api_key)
    if result:
        bot.say(result)
        parts = trigger.raw.split(None)
        parts = parts[:3]
        parts.append(':{0}'.format(result))
        string = ' '.join(parts)
        print(string)
        
        pt = PreTrigger(bot.nick, string)
        bot.dispatch(pt)

    else:
        bot.reply('No results found for \'{0}\'.'.format(query))

@commands('duck', 'ddg')
@example('.duck privacy or .duck !mcwiki obsidian')
def duck(bot, trigger):
    """Queries Duck Duck Go for the specified input."""
    query = trigger.group(2)
    if not query:
        return bot.reply('.ddg what?')

    # If the API gives us something, say it and stop
    result = duck_api(query)
    if result:
        bot.reply(result)
        return

    # Otherwise, look it up on the HTMl version
    uri = duck_search(query)

    if uri:
        bot.say(uri)
        bot.say(find_title(uri))
        if 'last_seen_url' in bot.memory:
            bot.memory['last_seen_url'][trigger.sender] = uri
    else:
        bot.reply("No results found for '%s'." % query)

@commands('suggest')
def suggest(bot, trigger):
    """Suggest terms starting with given input"""
    if not trigger.group(2):
        return bot.reply("No query term.")
    query = trigger.group(2)
    uri = 'http://websitedev.de/temp-bin/suggest.pl?q='
    answer = requests.get(uri + query.replace('+', '%2B')).text
    if answer:
        bot.say(answer)
    else:
        bot.reply('Sorry, no result.')
