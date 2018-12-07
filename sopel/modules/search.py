# coding=utf-8
# Copyright 2008-9, Sean B. Palmer, inamidst.com
# Copyright 2012, Elsie Powell, embolalia.com
# Licensed under the Eiffel Forum License 2.


import re
import requests
from sopel.module import commands, example
from sopel.trigger import PreTrigger
import json
import requests
import xmltodict
import sys

from sopel.modules.url import find_title

if sys.version_info.major < 3:
    from urllib import quote_plus, unquote as _unquote
    unquote = lambda s: _unquote(s.encode('utf-8')).decode('utf-8')
else:
    from urllib.parse import quote_plus, unquote

r_entity = re.compile(r'&([^;\s]+);')
user_agent = None

def setup(bot):
    global user_agent
    try:
        user_agent = bot.config.url.user_agent
    except:
        pass

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

def google(query, key):
    url = 'https://www.googleapis.com/customsearch/v1'
    data = requests.get(url, params={'key' : key, 'cx': '005137987755203522487:jb4yson7hu0', 'q' : query}).json()
    if 'items' not in data:
        return None
    results = data['items']
    return decode(results[0]['link'])


r_duck = re.compile(r'nofollow" class="[^"]+" href="(?!(?:https?:\/\/r\.search\.yahoo)|(?:https?:\/\/duckduckgo\.com\/y\.js)(?:\/l\/\?kh=-1&amp;uddg=))(.*?)">')

def duck_search(query):
    query = query.replace('!', '')
    uri = 'https://duckduckgo.com/html/?q=%s&kl=uk-en' % query
    bytes = requests.get(uri, headers={'User-Agent':user_agent}).text
    if 'web-result' in bytes:  # filter out the adds on top of the page
        bytes = bytes.split('web-result')[1]
    m = r_duck.search(bytes)
    if m:
        unquoted_m = unquote(m.group(1))
        return web.decode(unquoted_m)

def duck_api(query):
    if '!bang' in query.lower():
        return 'https://duckduckgo.com/bang.html'

    # This fixes issue #885 (https://github.com/sopel-irc/sopel/issues/885)
    # It seems that duckduckgo api redirects to its Instant answer API html page
    # if the query constains special charactares that aren't urlencoded.
    # So in order to always get a JSON response back the query is urlencoded
    query = quote_plus(query)
    uri = 'https://api.duckduckgo.com/?q=%s&format=json&no_html=1&no_redirect=1' % query
    try:
        results = requests.get(uri).json()
    except ValueError:
        return None
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
        parts = parts[:4]
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
@example('.suggest ', 'No query term.')
@example('.suggest lkashdfiauwgeaef', 'Sorry, no result.')
@example('.suggest wikip', 'wikipedia')
def suggest(bot, trigger):
    """Suggest terms starting with given input"""
    if not trigger.group(2):
        return bot.reply("No query term.")
    query = trigger.group(2)
    # Using Google isn't necessarily ideal, but at most they'll be able to build
    # a composite profile of all users on a given instance, not a profile of any
    # single user. This can be switched out as soon as someone finds (or builds)
    # an alternative suggestion API.
    uri = 'https://suggestqueries.google.com/complete/search?output=toolbar&hl=en&q='
    answer = xmltodict.parse(requests.get(uri + query.replace('+', '%2B')).text)['toplevel']
    try:
        answer = answer['CompleteSuggestion'][0]['suggestion']['@data']
    except TypeError:
        answer = None
    if answer:
        bot.say(answer)
    else:
        bot.reply('Sorry, no result.')
