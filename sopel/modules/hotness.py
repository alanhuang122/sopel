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

@commands('gay')
def gay_command(bot,trigger):
    if not trigger.group(2):
        nick = trigger.nick
    else:
        nick = trigger.group(2).strip()
    val = bot.db.get_nick_value(nick, 'gay')
    if not val:
        rand = randint(0, 6)
        bot.say('Kinsey Scale Rating: {0}/6'.format(rand))
    else:
        bot.say('Kinsey Scale Rating: {0}/6'.format(val))

@commands('kinsey')
def kinsey_set(bot, trigger):
    '''Set a value for the .gay command.'''
    if not trigger.group(2):
        bot.db.set_nick_value(trigger.nick, 'gay', None)
        bot.say('Value cleared.')
        return
    if trigger.group(2).lower() == 'x':
        val = 'X'
    else:
        try:
            val = int(trigger.group(2))
            assert val < 7 and val > -1
        except:
            bot.say('Enter a valid value [0-6] or X')
            return
    bot.db.set_nick_value(trigger.nick, 'gay', val)
    bot.say('Value set.')
