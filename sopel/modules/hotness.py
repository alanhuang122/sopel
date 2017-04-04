from random import randint
from sopel.module import commands, example

@commands('hot', 'hotness')
def hot_command(bot, trigger):
    """Find out how hot something is"""
    rand = randint(0, 10)
    if rand == 10 and randint(0,1) == 0:
        bot.say('Hotness: 5/7 (perfect)')
    else:
        bot.say('Hotness: {0}/10'.format(rand))
        if randint(0,2) == 0:
            bot.say('{0}/10 with rice'.format(randint(0,10)))

@commands('gay', 'kinsey')
def gay_command(bot,trigger):
    rand = randint(0, 6)
    bot.say('Kinsey Scale Rating: {0}/6'.format(rand))
