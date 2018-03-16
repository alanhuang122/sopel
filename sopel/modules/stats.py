# coding=utf-8
"""
stats.py - Advanced stats module for Sopel IRC bot.
Author: Dennis Whitney
Handle: minsis
Email: dwhitney@irunasroot.com

Copyright © 2016, Dennis Whitney <dwhitney@irunasroot.com>
Licensed under the Eiffel Forum License 2.
"""



from sopel.module import commands

@commands("stats")
def stats_command(bot, trigger):
    if trigger.sender == '#fallenlondon' or trigger.sender == '#alantest':
        bot.say('Cumulative: https://alanhua.ng/pisg.html | This Month: https://alanhua.ng/pisg-monthly.html | This Week: https://alanhua.ng/pisg-weekly.html')

    else:
        print(trigger.sender)
