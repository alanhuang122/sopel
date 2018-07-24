#!/usr/local/bin/python
#coding: latin-1

from sopel.module import commands
from sopel.modules.emoticons import taunt_command as taunt

@commands('horoscope')
def horoscope_command(bot, trigger):
    taunt(bot, trigger)
    return
