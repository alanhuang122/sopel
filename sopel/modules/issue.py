#!/usr/local/bin/python
#coding: latin-1

from sopel.module import commands

@commands('issue')
def issue_command(bot, trigger):
    """Report problems with the bot"""
    if trigger.group(2):
        bot.say("Issue \"{0}\" filed to /dev/null".format(trigger.group(2)))
        with open('/home/alan/.sopel/issues', 'a') as file:
            file.write(trigger.raw)
            file.close()
