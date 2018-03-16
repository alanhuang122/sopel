
from sopel.module import commands, example, NOLIMIT, rule, require_chanmsg

@require_chanmsg(message='Sorry, because of recent abuse, changing karma is not allowed in PMs.')
@rule('\+1 (\w*)')
@example('+1 nick')
def plusincreaseKarma(bot, trigger):
    if not trigger.group(1):
        return NOLIMIT

    name = trigger.group(1).strip()
   
    currentKarma = bot.db.get_nick_value(name, 'karma')
    if not currentKarma:
        currentKarma = 0
    else:
        currentKarma = int(currentKarma)
    if trigger.nick == name and not trigger.nick == 'Alan':
        bot.say("No changing your own karma.")
        return
    if not name == 'phy1729':
        currentKarma += 1

    bot.db.set_nick_value(name, 'karma', currentKarma)
#    bot.reply("One karma point given to " + trigger.group(1))

@require_chanmsg(message='Sorry, because of recent abuse, changing karma is not allowed in PMs.')
@rule('\-1 (\w*)')
@example('-1 nick')
def minusreduceKarma(bot, trigger):
    if not trigger.group(1):
        return NOLIMIT

    name = trigger.group(1).strip()
   
    currentKarma = bot.db.get_nick_value(name, 'karma')
    if not currentKarma:
        currentKarma = 0
    else:
        currentKarma = int(currentKarma)
    if trigger.nick == name and not trigger.nick == 'Alan':
        bot.say("No changing your own karma.")
        return
    if not name == 'phy1729':
        currentKarma -= 1

    bot.db.set_nick_value(name, 'karma', currentKarma)
#    bot.reply("One karma point taken from " + trigger.group(1))

@require_chanmsg(message='Sorry, because of recent abuse, changing karma is not allowed in PMs.')
@rule('^(\w*)\+\+$')
@example('nick++')
def increaseKarma(bot, trigger):
    if not trigger.group(1):
        return NOLIMIT

    name = trigger.group(1).strip()
   
    currentKarma = bot.db.get_nick_value(name, 'karma')
    if not currentKarma:
        currentKarma = 0
    else:
        currentKarma = int(currentKarma)
    if trigger.nick == name and not trigger.nick == 'Alan':
        bot.say("No changing your own karma.")
        return
    if not name == 'phy1729':
        currentKarma += 1

    bot.db.set_nick_value(name, 'karma', currentKarma)
 #   bot.reply("One karma point given to " + trigger.group(1))

@require_chanmsg(message='Sorry, because of recent abuse, changing karma is not allowed in PMs.')
@rule('^(\w*)\-\-$')
@example('nick--')
def reduceKarma(bot, trigger):
    if not trigger.group(1):
        return NOLIMIT

    name = trigger.group(1).strip()
   
    currentKarma = bot.db.get_nick_value(name, 'karma')
    if not currentKarma:
        currentKarma = 0
    else:
        currentKarma = int(currentKarma)
    if trigger.nick == name and not trigger.nick == 'Alan':
        bot.say("No changing your own karma.")
        return
    if not name == 'phy1729':
        currentKarma -= 1

    bot.db.set_nick_value(name, 'karma', currentKarma)
#    bot.reply("One karma point taken from " + trigger.group(1))
    
@commands('karma')
@example('.karma [nick]')
def tellKarma(bot, trigger):
    """Outputs user's number of karma points."""
    if not trigger.group(2):
        nick = 'You'
        reply = " have "
    else:
        nick = trigger.group(2).strip()
        reply = " has "

    currentKarma = bot.db.get_nick_value(nick, 'karma')
    if not currentKarma:
        currentKarma = '0'
    bot.say("{}{}{} karma points.".format(nick, reply, currentKarma))

@commands('top')
@example('.top 5')
def topKarma(bot, trigger):
    """Outputs users with highest karma"""
    if not trigger.group(2):
        num = 5
    else:
        try:
            num = int(trigger.group(2))
        except ValueError:
            num = 5
    currentKarmas = []
    for user in bot.users:
        karma = bot.db.get_nick_value(user, 'karma')
        if karma is not None:
            currentKarmas.append({'name': user, 'karma': karma})
    topKarma = sorted(currentKarmas, key=lambda k: k['karma'], reverse=True)
    reply = "The top " + str(num) + " karma scores are: "
    for x in range(0, num):
        if x >= len(topKarma):
            break
        reply += (topKarma[x]['name'] + ": " + str(topKarma[x]['karma']) + ", ")
    reply = reply[:-2]
    bot.say(reply)
