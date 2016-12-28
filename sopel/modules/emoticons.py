#!/usr/bin/python
#coding: utf-8

from sopel.module import commands, example
import json
from random import randint
import operator
def setup(bot):
    global stats
    stats = json.load(open('/home/ec2-user/.sopel/stats'))


def save():
    f = open('/home/ec2-user/.sopel/stats', 'w')
    f.write(json.dumps(stats))


@commands('stats')
def stats_command(bot, trigger):
    if not trigger.group(2):
        slist = sorted(stats.items(), key=operator.itemgetter(1),reverse=True)
        msg = u'Top 5 emotes used: '
        for i in range(5):
            msg += '{0}: {1}, '.format(slist[i][0],slist[i][1])
        msg = msg[:-2]
        bot.say(msg)
        return
    if trigger.group(2) in stats:
        bot.say('{0} has been used {1} times.'.format(trigger.group(2), stats[trigger.group(2)]))
    else:
        bot.say('Stats not found.')
    stats['stats'] += 1
    save()


@commands('stare')
def stare_command(bot, trigger):
    if not trigger.group(2):
        bot.say('{0}: \xe0\xb2\xa0_\xe0\xb2\xa0'.format(trigger.nick))
    else:
        bot.say('{0}: \xe0\xb2\xa0_\xe0\xb2\xa0'.format(trigger.group(2)))
    stats['stare'] += 1
    save()


@commands('lenny')
def lenny_command(bot, trigger):
    if not trigger.group(2):
        bot.say('{0}: ( \xcd\xa1\xc2\xb0 \xcd\x9c\xca\x96 \xcd\xa1\xc2\xb0)'.format(trigger.nick))
    else:
        bot.say('{0}: ( \xcd\xa1\xc2\xb0 \xcd\x9c\xca\x96 \xcd\xa1\xc2\xb0)'.format(trigger.group(2)))
    stats['lenny'] += 1
    save()


@commands('shrug')
def shrug_command(bot, trigger):
    if not trigger.group(2):
        bot.say('{0}: \xc2\xaf\\_(\xe3\x83\x84)_/\xc2\xaf'.format(trigger.nick))
    else:
        bot.say('{0}: \xc2\xaf\\_(\xe3\x83\x84)_/\xc2\xaf'.format(trigger.group(2)))
    stats['shrug'] += 1
    save()


@commands('bear')
def bear_command(bot, trigger):
    if not trigger.group(2):
        bot.say('{0}: \xca\x95\xe2\x80\xa2\xe1\xb4\xa5\xe2\x80\xa2\xca\x94'.format(trigger.nick))
    else:
        bot.say('{0}: \xca\x95\xe2\x80\xa2\xe1\xb4\xa5\xe2\x80\xa2\xca\x94'.format(trigger.group(2)))
    stats['bear'] += 1
    save()


@commands('table')
def table_command(bot, trigger):
    if not trigger.group(2):
        bot.say('{0}: (\xe2\x95\xaf\xc2\xb0\xe2\x96\xa1\xc2\xb0\xef\xbc\x89\xe2\x95\xaf\xef\xb8\xb5 \xe2\x94\xbb\xe2\x94\x81\xe2\x94\xbb'.format(trigger.nick))
    else:
        bot.say('{0}: (\xe2\x95\xaf\xc2\xb0\xe2\x96\xa1\xc2\xb0\xef\xbc\x89\xe2\x95\xaf\xef\xb8\xb5 \xe2\x94\xbb\xe2\x94\x81\xe2\x94\xbb'.format(trigger.group(2)))
    stats['table'] += 1
    save()


@commands('replace')
def replace_command(bot, trigger):
    if not trigger.group(2):
        bot.say('{0}: \xe2\x94\xac\xe2\x94\x80\xe2\x94\xac\xe3\x83\x8e(\xe0\xb2\xa0_\xe0\xb2\xa0\xe3\x83\x8e)'.format(trigger.nick))
    else:
        bot.say('{0}: \xe2\x94\xac\xe2\x94\x80\xe2\x94\xac\xe3\x83\x8e(\xe0\xb2\xa0_\xe0\xb2\xa0\xe3\x83\x8e)'.format(trigger.group(2)))
    stats['replace'] += 1
    save()


@commands('angry')
def angry_command(bot, trigger):
    if not trigger.group(2):
        bot.say('{0}: (\xe3\x83\x8e\xe0\xb2\xa0\xe7\x9b\x8a\xe0\xb2\xa0)\xe3\x83\x8e\xe5\xbd\xa1\xe2\x94\xbb\xe2\x94\x81\xe2\x94\xbb'.format(trigger.nick))
    else:
        bot.say('{0}: (\xe3\x83\x8e\xe0\xb2\xa0\xe7\x9b\x8a\xe0\xb2\xa0)\xe3\x83\x8e\xe5\xbd\xa1\xe2\x94\xbb\xe2\x94\x81\xe2\x94\xbb'.format(trigger.group(2)))
    stats['angry'] += 1
    save()


@commands('defenestrate')
def throw_command(bot, trigger):
    if not trigger.group(2):
        bot.say('Who am I defenestrating?')
    elif trigger.group(2) == bot.nick:
        bot.say('Nuh-uh! D:')
    elif trigger.group(2) == trigger.nick:
        bot.say('| \xef\xb8\xb5(/\xc2\xb0\xe2\x96\xa1\xc2\xb0)/ <- {0}'.format(trigger.nick))
        stats['autodefenestrate'] += 1
    else:
        bot.say('{0}: \xef\xbc\x88\xe2\x95\xaf\xc2\xb0\xe2\x96\xa1\xc2\xb0\xef\xbc\x89\xe2\x95\xaf\xef\xb8\xb5| (\\ .o.)\\'.format(trigger.group(2)))
        stats['defenestrate'] += 1
    save()


@commands('autodefenestrate')
def throwing_command(bot, trigger):
    if not trigger.group(2) or trigger.group(2) == trigger.nick:
        bot.say('| \xef\xb8\xb5(/\xc2\xb0\xe2\x96\xa1\xc2\xb0)/ <- {0}'.format(trigger.nick))
        stats['autodefenestrate'] += 1
    else:
        bot.say('No autodefestrating others! >:c')
    save()


@commands('rat')
def rat_command(bot, trigger):
    if not trigger.group(2):
        bot.say('{0}: <:3D~'.format(trigger.nick))
    else:
        bot.say('{0}: <:3D~'.format(trigger.group(2)))
    stats['rat'] += 1
    save()


@commands('wink')
def wink_command(bot, trigger):
    if not trigger.group(2):
        bot.say('{0}: ( \xcd\xa1~ \xcd\x9c\xca\x96 \xcd\xa1\xc2\xb0)'.format(trigger.nick))
    else:
        bot.say('{0}: ( \xcd\xa1~ \xcd\x9c\xca\x96 \xcd\xa1\xc2\xb0)'.format(trigger.group(2)))
    stats['wink'] += 1
    save()


@commands('utd')
def whoosh_command(bot, trigger):
    bot.say('WHOOOOOOOOOOSH o/')
    stats['utd'] += 1
    save()


@commands('dev', 'developers')
def devs_command(bot, trigger):
    bot.say('DEVELOPERS DEVELOPERS DEVELOPERS DEVELOPERS')
    stats['dev'] += 1
    save()


@commands('poke')
def poke_command(bot, trigger):
    if not trigger.group(2):
        bot.action('pokes {0}'.format(trigger.nick))
    else:
        bot.action('pokes {0}'.format(trigger.group(2)))
    stats['poke'] += 1
    save()


@commands('fight')
def fight_command(bot, trigger):
    if not trigger.group(2):
        bot.say('{0}: (\xe0\xb8\x87\xe0\xb2\xa0_\xe0\xb2\xa0)\xe0\xb8\x87'.format(trigger.nick))
    else:
        bot.say('{0}: (\xe0\xb8\x87\xe0\xb2\xa0_\xe0\xb2\xa0)\xe0\xb8\x87'.format(trigger.group(2)))
    stats['fight'] += 1
    save()


@commands('flower')
def flower_command(bot, trigger):
    if not trigger.group(2):
        bot.say('{0}: (\xe2\x97\x95\xe2\x97\xa1\xe2\x97\x95)\xe3\x83\x8e\xe2\x9c\xbf'.format(trigger.nick))
    else:
        bot.say('{0}: (\xe2\x97\x95\xe2\x97\xa1\xe2\x97\x95)\xe3\x83\x8e\xe2\x9c\xbf'.format(trigger.group(2)))
    stats['flower'] += 1
    save()


@commands('pretty')
def pretty_command(bot, trigger):
    if not trigger.group(2):
        bot.say('{0}: (\xe2\x97\x95\xe2\x97\xa1\xe2\x97\x95\xe2\x9c\xbf)'.format(trigger.nick))
    else:
        bot.say('{0}: (\xe2\x97\x95\xe2\x97\xa1\xe2\x97\x95\xe2\x9c\xbf)'.format(trigger.group(2)))
    stats['pretty'] += 1
    save()


@commands('party')
def party_command(bot, trigger):
    if not trigger.group(2):
        bot.say('{0}: \xe2\x99\xaa\xef\xbc\xbc(*\xef\xbc\xbe\xe2\x96\xbd\xef\xbc\xbe*)\xef\xbc\x8f\xef\xbc\xbc(*\xef\xbc\xbe\xe2\x96\xbd\xef\xbc\xbe*)\xef\xbc\x8f'.format(trigger.nick))
    else:
        bot.say('{0}: \xe2\x99\xaa\xef\xbc\xbc(*\xef\xbc\xbe\xe2\x96\xbd\xef\xbc\xbe*)\xef\xbc\x8f\xef\xbc\xbc(*\xef\xbc\xbe\xe2\x96\xbd\xef\xbc\xbe*)\xef\xbc\x8f'.format(trigger.group(2)))
    stats['party'] += 1
    save()


@commands('why')
def explain_command(bot, trigger):
    if trigger.sender.lower() == '#fallenlondon' and randint(0, 1):
        bot.say('Who knowzz?')
    else:
        bot.reply("because fuck you, that's why")
    stats['why'] += 1
    save()


@commands('tentacle')
def tentacle_command(bot, trigger):
    if not trigger.group(2):
        bot.reply(u'~~~~~~~~~ （╯°□°）╯')
    else:
        bot.say('{0}: ~~~~~~~~~ （╯°□°）╯'.format(trigger.group(2)))
    stats['tentacle'] += 1
    save()


@commands('kirby', 'dance')
def dance_command(bot, trigger):
    if not trigger.group(2):
        bot.reply("(>'-')> <('-'<) ^('-')^ v('-')v(>'-')> (^-^)")
    else:
        bot.say("(>'-')> <('-'<) ^('-')^ v('-')v(>'-')> (^-^)".format(trigger.group(2)))
    stats['kirby'] += 1
    stats['dance'] += 1
    save()
