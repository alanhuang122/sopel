# coding=utf-8
"""
dictionary.py - Sopel Dictionary Module
Copyright 2017, Alan Huang
Licensed under the Eiffel Forum License 2.

http://sopel.chat
"""
from __future__ import unicode_literals, absolute_import, print_function, division
import requests, re, aspell
from sopel.module import commands, example

url = 'https://od-api.oxforddictionaries.com/api/v1'

def setup(bot):
    global app_id, app_key
    app_id = bot.config.dict.id
    app_key = bot.config.dict.key

def search(word):
    global app_id, app_key
    data = requests.get(url + '/search/en', params = {'q': word.lower(), 'limit': 1}, headers = {'app_id': app_id, 'app_key': app_key}).json()
    if data['results'] == []:
        return None
    return data['results'][0]['id']
    
def lookup(word):
#    s = aspell.Speller()
#    if not s.check(word):
#        if len(s.suggest(word)) is 0:
#            return "I couldn't find any definitions for that word."
#        word = s.suggest(word)[0]

    word_id = search(word)
    if word_id is None:
        return 'I couldn\'t find any definitions for that word.'

    global app_id, app_key
    data = requests.get(url + '/entries/en/' + word_id + '/definitions', headers = {'app_id' : app_id, 'app_key' : app_key})
    if data.status_code == 404:
        return 'I couldn\'t find that word.'
    data = data.json()
    defs = []
    word = data['results'][0]['word']
    lexicalEntries = data['results'][0]['lexicalEntries']
    count = len(lexicalEntries)
    limit = 400 / count

    for entry in lexicalEntries:
        temp = []
        for sub in entry['entries']:
            for sense in sub['senses']:
                temp.append(sense['definitions'][0])
                if 'subsenses' in sense:
                    for subsense in sense['subsenses']:
                        temp.append(subsense['definitions'][0])
        tempdefs = ['%s. %s' % (i + 1, e) for i, e in enumerate(temp)]
        slug = ', '.join(tempdefs)
#        while len(slug) > limit:
#            tempdefs = tempdefs[:-1]
#            slug = ', '.join(tempdefs)
#        if count != 1: #recalculate limit for remaining entries
#        limit = ((limit * count) - len(slug)) / (count - 1)
#            count -= 1
        defs.append('{0}: {1}'.format(entry['lexicalCategory'], slug))

    msg = '{0} — {1}'.format(word.lower(), ' — '.join(defs))
    return msg

@commands('define', 'dict', 'wt')
@example('.dict bailiwick')
def dictionary(bot, trigger):
    """Look up a word in the Oxford English Dictionary."""
    word = trigger.group(2)
    if word is None:
        bot.reply('You must tell me what to look up!')
        return

    msg = lookup(word)
    bot.say(msg)
    return
