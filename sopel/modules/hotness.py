# 2016.12.24 03:30:17 CST
#Embedded file name: modules/hotness.py
import random
from sopel.module import commands, example

@commands('hot', 'hotness')
def hot_command(bot, trigger):
    """Find out how hot something is"""
    rand = random.randint(0, 10)
    bot.say('Hotness: {0}/10'.format(rand))
