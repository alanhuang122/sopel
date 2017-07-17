# coding=utf-8
"""
stats.py - Advanced stats module for Sopel IRC bot.
Author: Dennis Whitney
Handle: minsis
Email: dwhitney@irunasroot.com

Copyright © 2016, Dennis Whitney <dwhitney@irunasroot.com>
Licensed under the Eiffel Forum License 2.
"""

from __future__ import unicode_literals, absolute_import, division, print_function

from sopel.module import commands

@commands("stats")
def stats_command(bot, trigger):
    if trigger.sender == '#fallenlondon' or trigger.sender == '#alantest':
        bot.say('Cumulative: https://alanhuang.name/pisg.html | This Month: https://alanhuang.name/pisg-monthly.html | This Week: https://alanhuang.name/pisg-weekly.html')

    else:
        print(trigger.sender)
