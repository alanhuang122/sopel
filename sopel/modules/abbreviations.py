#!/usr/bin/python
#coding: utf-8

import pickle
from sopel.module import commands
from fuzzywuzzy import fuzz, process

@commands('abb')
@commands('acr')
def lookup_command(bot, trigger):
    """Searches the FL wiki for an abbreviation."""
    data = pickle.load(open('/home/alan/.sopel/abbreviations', 'rb'))
    if not trigger.group(2):
        bot.say('What acronym do you want to look up?')
        return
    key = trigger.group(2).strip().upper()
    match = process.extractOne(key, list(data.keys()), scorer=fuzz.token_set_ratio)
    if match[1] < 85:
        bot.say('I don\'t think I have that acronym. Try .ud?')
        return
    bot.say(data[match[0]])
