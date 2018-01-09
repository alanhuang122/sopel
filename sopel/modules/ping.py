# coding=utf-8
"""
ping.py - Sopel Ping Module
Author: Sean B. Palmer, inamidst.com
About: https://sopel.chat
"""
from __future__ import unicode_literals, absolute_import, print_function, division

import random
from time import sleep
from datetime import datetime
from sopel.module import rule, priority, thread
from unidecode import unidecode


@rule(r'(?i)(hi|hello|hey),? $nickname[.! \t]*$')
def hello(bot, trigger):
    greeting = random.choice(('hi', 'hey there', 'hello'))
    punctuation = random.choice(('', '.'))
    bot.say(greeting + ' ' + trigger.nick + punctuation)


@rule(r'(?i)(fuck|screw) you( .+)?,? $nickname[.! \t]*$')
def rude(bot, trigger):
    bot.say("well fuck you too {0}".format(trigger.nick))


@rule('$nickname!')
@priority('high')
@thread(False)
def interjection(bot, trigger):
    bot.say(trigger.nick + '!')

@rule(r'(?i)(pats|pets) $nickname[. \t]*$')
@rule(r'(?i)(good bot)[. \t!]*$')
def praise(bot, trigger):
    evil = random.randint(0,4)
    if evil == 0:
        bot.say('>:3c')
    else:
        bot.say('^_^')

#@rule(r'(?i)(kisses) $nickname[ \t.]*$')
def kiss(bot, trigger):
    bot.say('o///o')

#@rule(r'(?i)(hugs) $nickname[ \t.]*$')
def affection(bot, trigger):
    bot.say('<3')

@rule(r'(?i)(kinkshames) $nickname[ \t.]*$')
def shame(bot, trigger):
    bot.say('Hey! >:c')

@rule(r'(?i)(lobotomizes|smacks|beats|hurts|stabs|punches|slaps|defenestrates|hits|kicks|whacks|whaps|abuses|molests) $nickname[ \t.]*$')
def hurt(bot,trigger):
    bot.say('D:')

@rule('(THAT)[\'\"]?(S NOT POSIX)[!. \t]*$')
def posix(bot, trigger):
    bot.reply('YOU\'RE NOT POSIX!')

@rule(r'(?i)(pokes) $nickname[ \t.]*$')
def poke(bot, trigger):
    response = random.choice(('?', 'Hmm?'))
    bot.say(response)

@rule(r'(?i)murders $nickname (\d+)(s|m|h)$')
def kill(bot, trigger):
    if trigger.owner:
        if trigger.group(2) == 's':
            time = int(trigger.group(1))
        elif trigger.group(2) == 'm':
            time = int(trigger.group(1)) * 60
        elif trigger.group(2) == 'h':
            time = int(trigger.group(1)) * 3600
        print('[ping] Dead for {0}s at {1}'.format(time, datetime.now().strftime('%H:%M:%S')))
        bot.say('x_x')
        bot.dead = True
        sleep(time)
        bot.dead = False
        print('[ping] Alive again')
    else:
        print('[ping] {0} tried to murder me...'.format(trigger.nick))

#@rule(r'.*')
def hooboo(bot, trigger):
    try:
        string = trigger.group(0)
    except IndexError:
        return
    if 'hooboo' in string:
        bot.say('Don\'t call me "hooboo" >:c')
        return
    else:
        converted = unidecode(string)
        converted = converted.replace('0', 'o')
        if 'hooboo' in converted:
            bot.say('Don\'t call me "hooboo", you sneaky bugger >:c!!!')
            return

@rule(r'.*')
def log_PMs(bot, trigger):
    if trigger.is_privmsg:
        print('[ping] received privmsg: {}'.format(trigger.raw))

@rule(r'(?i).*\ba[ow]oo+\b.*')
def awoo(bot, trigger):
    bot.say(random.choice(['awoooo; OwO', 'DON\'T AWOO - $300 PENALTY']))
