# coding=utf-8
"""
translate.py - Sopel Translation Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright © 2013-2014, Elad Alfassa <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.

https://sopel.chat
"""
from __future__ import unicode_literals, absolute_import, print_function, division
from sopel.module import commands, example
import os, sys, re
from google.cloud import translate

if sys.version_info.major >= 3:
    unicode = str

def setup(bot):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/alan/.sopel/sopel-irc-key.json'
    global client, languages
    client = translate.Client()
    languages = client.get_languages()

#todo: have .lang for supported languages - reverse search with fuzzywuzzy

@commands('lang')
def lang(bot, trigger):
    """Look up a language or language code"""
    if not trigger.group(2):
        bot.say('I support: {0}'.format(', '.join(x['language'] for x in languages)))
        return
    if 'chinese' in trigger.group(2).lower() or 'zh' in trigger.group(2).lower():
        bot.say('Chinese (Simplified): zh; Chinese (Traditional): zh-TW')
        return
    for entry in languages:
        if trigger.group(2).lower() == entry['language'].lower() or trigger.group(2).lower() == entry['name'].lower():
            bot.say('{0}: {1}'.format(entry['name'], entry['language']))
            return

    bot.say('Language not found.')

def lookup(string):
    if 'chinese' in string.lower() or 'zh' in string.lower():
        return 'zh'
    for entry in languages:
        if string.lower() == entry['language'].lower() or string.lower() == entry['name'].lower():
            return entry['language']

    return None

@commands('translate', 'tr')
@example('.tr :de omelette du fromage')
def tl(bot, trigger):
    global languages
    """Translates a phrase using Google Translate. Defaults to English."""
    command = trigger.group(2)
    if not command:
        bot.reply('What am I translating?')
    s = None
    t = 'en'
    parts = command.rsplit(None, 4)
    print(parts)
    if len(parts) > 4:
        if parts[3] == 'from':
            s = lookup(parts[4])
            parts = parts[:-2]
        elif parts[3] == 'to':
            t = lookup(parts[4])
            parts = parts[:-2]
    if len(parts) > 2:
        if parts[1] == 'from':
            s = lookup(parts[2])
            parts = parts[:-2]
        elif parts[1] == 'to':
            t = lookup(parts[2])
            parts = parts[:-2]
    client = translate.Client()
    if s:
        print('3')
        translation = client.translate(' '.join(parts), target_language=t, source_language=s)
    else:
        print('2')
        translation = client.translate(' '.join(parts), target_language=t)

    bot.reply(u'"{0}" ({1} to {2})'.format(re.sub('&#39;','\'',translation['translatedText']), s if s is not None else translation['detectedSourceLanguage'], t))
