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
import os, sys
from google.cloud import translate

if sys.version_info.major >= 3:
    unicode = str

def setup(bot):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/ec2-user/google-cloud-sdk/sopel-irc-key.json'

#todo: have .lang for supported languages - reverse search with fuzzywuzzy

@commands('translate', 'tr')
@example('.tr :de omelette du fromage')
def tl(bot, trigger):
    """Translates a phrase using Google Translate. Defaults to English."""
    command = trigger.group(2)

    if not command:
        bot.reply('What am I translating?')

    targetlang = 'en'

    test = command.split(None, 1)

    if test[0].startswith(':'):
        targetlang = test[0][1:]  #strips initial colon from string

    client = translate.Client()

    translation = client.translate(test[1], target_language=targetlang)

    bot.reply('"{0}" ({1} to {2})'.format(translation['translatedText'], translation['detectedSourceLanguage'], targetlang))
