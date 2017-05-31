#!/usr/local/bin/python
#coding: latin-1

from sopel.module import commands
import imp

emoticons = imp.load_source('emoticons', '/home/ec2-user/.sopel/modules')

@commands('horoscope')
def horoscope_command(bot, trigger):
    emoticons.taunt_command(bot,trigger)
    return
