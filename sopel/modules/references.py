# coding=utf-8
# Copyright 2008-9, Sean B. Palmer, inamidst.com
# Copyright 2012, Elsie Powell, embolalia.com
# Licensed under the Eiffel Forum License 2.
from __future__ import unicode_literals, absolute_import, print_function, division

from sopel.module import commands
from sopel.trigger import PreTrigger
import os

dir = '/home/alan/references/links/'

@commands('reference', 'ref')
def reference(bot, trigger):
    query = trigger.group(2)
    files = os.listdir(dir)
    if not query:
        bot.say(str(files))
        return
    if query in files:
        link = open(dir + query).read()
        bot.say(link)

        parts = trigger.raw.split(None)
        parts = parts[:4]
        parts.append(':{0}'.format(link))
        string = ' '.join(parts)
        print(string)
#        urls = process_urls(bot, trigger, link)
#        print(urls)
        pt = PreTrigger(bot.nick, string)
        bot.dispatch(pt)
    else:
        bot.say("Not found")
