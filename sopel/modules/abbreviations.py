#!/usr/bin/python
#coding: utf-8

from sopel.module import commands, example
import pickle
from fuzzywuzzy import fuzz, process
def setup(bot):
    global data
    with open('/home/ec2-user/.sopel/abbreviations') as dictionary:
        data = pickle.loads(dictionary.read())

@commands('abb')
@commands('acr')
def lookup_command(bot, trigger):
    """Searches the FL wiki for an abbreviation."""
    global data
    if not trigger.group(2):
        bot.say('What acronym do you want to look up?')
        return
    key = trigger.group(2).strip().upper()
    match = process.extractOne(key,data.keys(),scorer=fuzz.token_set_ratio)
    if match[1] < 80:
        bot.say('I don\'t think I have that acronym.')
        return
    bot.say(data[match[0]])
