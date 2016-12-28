# 2016.12.24 03:32:20 CST
#Embedded file name: modules/posix.py
from sopel.module import commands, example

@commands('posix')
def posix_command(bot, trigger):
    """Is it POSIX?"""
    if not trigger.group(2):
        bot.say("THAT'S NOT POSIX")
    else:
        bot.say("{0}: YOU'RE NOT POSIX".format(trigger.group(2)))
