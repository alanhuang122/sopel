#!/usr/local/bin/python
#coding: latin-1

from sopel.module import commands
from sopel.modules import emoticons

@commands('horoscope')
def horoscope_command(bot, trigger):
    emoticons.taunt_command(bot,trigger)
    return
