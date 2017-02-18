# coding=utf-8
"""
translate.py - Sopel Translation Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright © 2013-2014, Elad Alfassa <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.

http://sopel.chat
"""
from __future__ import unicode_literals, absolute_import, print_function, division
from sopel import web
from sopel.module import rule, commands, priority, example
import os, sys, re
from google.cloud import translate

if sys.version_info.major >= 3:
    unicode = str

def setup(bot):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/ec2-user/google-cloud-sdk/sopel-irc-key.json'
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
    match = re.match(r'.*\b(to (.+?))\b.*', command)
    if not command:
        bot.reply('What am I translating?')

    targetlang = 'en'
    string = command
    test = command.split(None, 1)
    print(match)
    if test[0].startswith(':'):
        targetlang = test[0][1:]  #strips initial colon from string
        string = test[1]
        if targetlang not in ' '.join(x['language'] for x in languages):
            bot.say('Unrecognized/unsupported target language.')
            return
    elif match:
        targetlang = lookup(match.group(2))
        if targetlang is None:
            targetlang = 'en'
        else:
            string = re.sub(match.group(1), '', command)

    client = translate.Client()
    translation = client.translate(string, target_language=targetlang)

    bot.reply(u'"{0}" ({1} to {2})'.format(translation['translatedText'], translation['detectedSourceLanguage'], targetlang))
