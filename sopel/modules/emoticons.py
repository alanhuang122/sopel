#!/usr/bin/python
#coding: utf-8

from sopel.module import commands, example
import json
from random import randint
import operator
import re
def setup(bot):
    global stats
    stats = json.load(open('/home/ec2-user/.sopel/stats'))
    unicode_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
    global regex
    regex = re.compile('[%s]' % re.escape(unicode_chars))

def clean(s):
    return regex.sub('',s)


def save():
    f = open('/home/ec2-user/.sopel/stats', 'w')
    f.write(json.dumps(stats))
    f.close()
    return


@commands('stats')
def stats_command(bot, trigger):
    if not trigger.group(2):
        slist = sorted(stats.items(), key=operator.itemgetter(1),reverse=True)
        msg = u'Top 5 emotes used: '
        for i in range(5):
            msg += '{0}: {1}, '.format(slist[i][0],slist[i][1])
        msg = msg[:-2]
        bot.say(msg)
    elif trigger.group(2).strip() in stats:
        bot.say(u'{0} has been used {1} times.'.format(trigger.group(2).strip(), stats[trigger.group(2).strip()]))
    else:
        bot.say(u'Stats not found.')
    stats['stats'] += 1
    save()
    return


@commands('stare')
def stare_command(bot, trigger):
    if not trigger.group(2):
        bot.say(u'{0}: ಠ_ಠ'.format(trigger.nick))
    else:
        bot.say(u'{0}: ಠ_ಠ'.format(clean(trigger.group(2).strip())))
    stats['stare'] += 1
    save()
    return


@commands('lenny')
def lenny_command(bot, trigger):
    if not trigger.group(2):
        bot.say(u'{0}: ( ͡° ͜ʖ ͡°)'.format(trigger.nick))
    else:
        bot.say(u'{0}: ( ͡° ͜ʖ ͡°)'.format(clean(trigger.group(2).strip())))
    stats['lenny'] += 1
    save()
    return

@commands('shrug')
def shrug_command(bot, trigger):
    if not trigger.group(2):
        bot.say(u'{0}: ¯\\_(ツ)_/¯'.format(trigger.nick))
    else:
        bot.say(u'{0}: ¯\\_(ツ)_/¯'.format(clean(trigger.group(2).strip())))
    stats['shrug'] += 1
    save()
    return

@commands('bear')
def bear_command(bot, trigger):
    if not trigger.group(2):
        bot.say(u'{0}: ʕ•ᴥ•ʔ'.format(trigger.nick))
    else:
        bot.say(u'{0}: ʕ•ᴥ•ʔ'.format(clean(trigger.group(2).strip())))
    stats['bear'] += 1
    save()
    return

@commands('table')
def table_command(bot, trigger):
    if not trigger.group(2):
        bot.say(u'{0}: (╯°□°)╯︵ ┻━┻'.format(trigger.nick))
    else:
        bot.say(u'{0}: (╯°□°)╯︵ ┻━┻'.format(clean(trigger.group(2).strip())))
    stats['table'] += 1
    save()
    return

@commands('replace')
def replace_command(bot, trigger):
    if not trigger.group(2):
        bot.say(u'{0}: ┬─┬ ノ( ゜-゜ノ)'.format(trigger.nick))
    else:
        bot.say(u'{0}: ┬─┬ ノ( ゜-゜ノ)'.format(clean(trigger.group(2).strip())))
    stats['replace'] += 1
    save()
    return

@commands('angry')
def angry_command(bot, trigger):
    if not trigger.group(2):
        bot.say(u'{0}: (ノಠ益ಠ)ノ彡┻━┻'.format(trigger.nick))
    else:
        bot.say(u'{0}: (ノಠ益ಠ)ノ彡┻━┻'.format(clean(trigger.group(2).strip())))
    stats['angry'] += 1
    save()
    return

@commands('defenestrate')
def throw_command(bot, trigger):
    if not trigger.group(2):
        bot.say(u'Who am I defenestrating?')
    elif clean(trigger.group(2).strip()) == bot.nick:
        bot.say(u'Nuh-uh! D:')
    elif clean(trigger.group(2).strip()) == trigger.nick:
        bot.say(u'| ︵(/°□°)/ <- {0}'.format(trigger.nick))
        stats['autodefenestrate'] += 1
    else:
        bot.say(u'{0}:  （╯°□°）╯︵| (\\ .o.)\\'.format(clean(trigger.group(2).strip())))
        stats['defenestrate'] += 1
    save()
    return

@commands('autodefenestrate')
def throwing_command(bot, trigger):
    if not trigger.group(2) or clean(trigger.group(2).strip()) == trigger.nick:
        bot.say(u'| ︵(/°□°)/ <- {0}'.format(trigger.nick))
        stats['autodefenestrate'] += 1
    else:
        bot.say(u'No autodefestrating others! >:c')
    save()
    return

@commands('rat')
def rat_command(bot, trigger):
    if not trigger.group(2):
        bot.say(u'{0}: <:3D~'.format(trigger.nick))
    else:
        bot.say(u'{0}: <:3D~'.format(clean(trigger.group(2).strip())))
    stats['rat'] += 1
    save()
    return

@commands('wink')
def wink_command(bot, trigger):
    if not trigger.group(2):
        bot.say(u'{0}: ( ͡~ ͜ʖ ͡°)'.format(trigger.nick))
    else:
        bot.say(u'{0}: ( ͡~ ͜ʖ ͡°)'.format(clean(trigger.group(2).strip())))
    stats['wink'] += 1
    save()
    return

@commands('utd')
def whoosh_command(bot, trigger):
    bot.say(u'WHOOOOOOOOOOSH o/')
    stats['utd'] += 1
    save()
    return

@commands('dev', 'developers')
def devs_command(bot, trigger):
    bot.say(u'DEVELOPERS DEVELOPERS DEVELOPERS DEVELOPERS')
    stats['dev'] += 1
    save()
    return

@commands('poke')
def poke_command(bot, trigger):
    if not trigger.group(2):
        bot.action('pokes {0}'.format(trigger.nick))
    else:
        bot.action('pokes {0}'.format(clean(trigger.group(2).strip())))
    stats['poke'] += 1
    save()
    return

@commands('fight')
def fight_command(bot, trigger):
    if not trigger.group(2):
        bot.say(u'{0}: (งಠ_ಠ)ง'.format(trigger.nick))
    else:
        bot.say(u'{0}: (งಠ_ಠ)ง'.format(clean(trigger.group(2).strip())))
    stats['fight'] += 1
    save()
    return

@commands('flower')
def flower_command(bot, trigger):
    if not trigger.group(2):
        bot.say(u'{0}: (◕◡◕)ノ✿'.format(trigger.nick))
    else:
        bot.say(u'{0}: (◕◡◕)ノ✿'.format(clean(trigger.group(2).strip())))
    stats['flower'] += 1
    save()
    return

@commands('pretty')
def pretty_command(bot, trigger):
    if not trigger.group(2):
        bot.say(u'{0}: (◕◡◕✿)'.format(trigger.nick))
    else:
        bot.say(u'{0}: (◕◡◕✿)'.format(clean(trigger.group(2).strip())))
    stats['pretty'] += 1
    save()
    return

@commands('party')
def party_command(bot, trigger):
    if not trigger.group(2):
        bot.say(u'{0}: ♪＼(*＾▽＾*)／＼(*＾▽＾*)／'.format(trigger.nick))
    else:
        bot.say(u'{0}: ♪＼(*＾▽＾*)／＼(*＾▽＾*)／'.format(clean(trigger.group(2).strip())))
    stats['party'] += 1
    save()
    return

@commands('why')
def explain_command(bot, trigger):
    if trigger.sender.lower() == '#fallenlondon' and randint(0, 1):
        bot.say(u'Who knowzz?')
    else:
        if trigger.nick == 'phy1729':
            bot.reply(u'because fuck you, that\'s why')
        elif randint(1,5) == 1:
            bot.say("THERE IS AS YET INSUFFICIENT DATA FOR A MEANINGFUL ANSWER")
        else:
            bot.reply(u'because fuck you, that\'s why')
    stats['why'] += 1
    save()
    return

@commands('tentacle')
def tentacle_command(bot, trigger):
    if not trigger.group(2):
        bot.reply(u'~~~~~~~~~ （╯°□°）╯')
    else:
        bot.say(u'{0}: ~~~~~~~~~ （╯°□°）╯'.format(clean(trigger.group(2).strip())))
    stats['tentacle'] += 1
    save()
    return

@commands('kirby', 'dance')
def dance_command(bot, trigger):
    if not trigger.group(2):
        bot.reply("(>'-')> <('-'<) ^('-')^ v('-')v(>'-')> (^-^)")
    else:
        bot.say("{0}: (>'-')> <('-'<) ^('-')^ v('-')v(>'-')> (^-^)".format(clean(trigger.group(2).strip())))
    stats['kirby'] += 1
    stats['dance'] += 1
    save()
    return

@commands('tem', 'temmie')
def hoi_command(bot, trigger):
    if not trigger.group(2):
        bot.reply(u'hOI!!!!!')
    else:
        bot.say(u'{0}: hOI!!!!!'.format(clean(trigger.group(2).strip())))
    stats['tem'] += 1
    stats['temmie'] += 1
    save()
    return
