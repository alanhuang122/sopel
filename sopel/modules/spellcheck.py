# coding=utf-8

import aspell, re, string
from sopel.module import commands

def setup(bot):
    chars = string.letters
    global regex
    regex = re.compile('[^%s]' % re.escape(chars))

def clean(s):
    return regex.sub('',s)

@commands('add')
def add_command(bot, trigger):
    if trigger.owner:
        c = aspell.Speller('lang', 'en')
        c.addtoPersonal(trigger.group(2))
        c.saveAllwords()
        bot.say('Added {0}.'.format(trigger.group(2)))
    else:
        bot.say('I only trust {0} to add words >:c'.format(bot.config.core.owner))

def check_multiple(bot, words):
    mistakes = []

    c = aspell.Speller('lang', 'en')
    for word in words:
        if not c.check(clean(word)):
            mistakes.append(clean(word))

    if len(mistakes) == 0:
        bot.say("Nothing seems to be misspelled.")
    else:
        bot.say('The following word(s) seem to be misspelled: {0}'.format(', '.join(['"{0}"'.format(w) for w in mistakes])))

def check_one(bot, word):
    c = aspell.Speller('lang', 'en')
    if c.check(clean(word)):
        bot.say("I don't see any problems with that word.")
        return
    else:
        suggestions = c.suggest(word)[:5]
    
    if len(suggestions) == 0:
        bot.say("That doesn't seem to be correct.")
    else:
        bot.say("That doesn't seem to be correct. Try {0}.".format(', '.join(['"{0}"'.format(s) for s in suggestions])))

@commands('spell', 'check', 'spellcheck')
def spellchecker(bot, trigger):
    if not trigger.group(2):
        bot.say('What word am I checking?')
        return

    if trigger.group(2) == bot.nick:
        bot.say('Hey, that\'s my name! Nothing wrong with it.')
        return
    
    words = trigger.group(2).split(None)

    if len(words) > 1:
        check_multiple(bot, words)

    else:
        check_one(bot, trigger.group(2))
