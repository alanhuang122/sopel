# coding=utf-8
"""
lmgtfy.py - Sopel Let me Google that for you module
Copyright 2013, Dimitri Molenaars http://tyrope.nl/
Licensed under the Eiffel Forum License 2.

https://sopel.chat/
"""

from sopel.module import commands


@commands('lmgtfy', 'lmgify', 'gify', 'gtfy')
def googleit(bot, trigger):
    """Let me just... google that for you."""
    #No input
    if not trigger.group(2):
        return bot.say('https://google.com/')
    bot.say('https://lmgtfy.com/?q=' + trigger.group(2).replace(' ', '+'))
