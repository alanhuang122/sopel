#!/usr/bin/python
#coding: utf-8

from sopel.module import commands
import json
from random import randint, choice
import operator
import re
def setup(bot):
    global stats
    stats = json.load(open('/home/alan/.sopel/stats'))
    unicode_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
    global regex
    regex = re.compile('[%s]' % re.escape(unicode_chars))

def clean(s):
    return regex.sub('',s)


def save():
    f = open('/home/alan/.sopel/stats', 'w')
    f.write(json.dumps(stats))
    f.close()
    return


@commands('estats')
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
    elif 'alan' in trigger.group(2).lower() and 'salaxalans' not in trigger.group(2).lower():
        return
    elif bot.nick.lower() in trigger.group(2).lower():
        bot.say(u'(◕◡◕✿)')
    else:
        bot.say(u'{0}: (◕◡◕)ノ✿'.format(clean(trigger.group(2).strip())))
    stats['flower'] += 1
    save()
    return

@commands('pretty')
def pretty_command(bot, trigger):
    if not trigger.group(2):
        bot.say(u'{0}: (◕◡◕✿)'.format(trigger.nick))
    elif 'alan' in trigger.group(2).lower() and 'salaxalans' not in trigger.group(2).lower():
        return
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

    if trigger.nick == 'phy1729' or trigger.nick == 'Alan':
        bot.reply(u'because fuck you, that\'s why')
    else:
        if randint(1,5) == 1:
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

@commands('finger')
def finger_command(bot, trigger):
    if not trigger.group(2):
        bot.reply(u'(☞ﾟヮﾟ)☞')
    else:
        bot.say(u'{0}: (☞ﾟヮﾟ)☞'.format(clean(trigger.group(2).strip())))
    if 'finger' not in stats:
        stats['finger'] = 0
    stats['finger'] += 1
    save()
    return

@commands('wonk')
def wonk_command(bot, trigger):
    bot.say(u':O')
    if 'wonk' not in stats:
        stats['wonk'] = 0
    stats['wonk'] += 1
    save()
    return

@commands('wank')
def wank_command(bot, trigger):
    bot.say(u'Ewwww...')
    if 'wank' not in stats:
        stats['wank'] = 0
    stats['wank'] += 1
    save()
    return

treats = ['a cupcake', 'a donut', 'an éclair', 'froyo', 'gingerbread', 'honeycomb', 'an ice cream sandwich', 'jellybeans', 'a kitkat', 'a lollipop', 'marshmallow', 'nougat', 'an oreo']

@commands('treat')
def treat_command(bot, trigger):
    bot.say("Oooh, {0}!".format(choice(treats)))
    if 'treat' not in stats:
        stats['treat'] = 0
    stats['treat'] += 1
    save()
    return

@commands('praise')
def praise_command(bot, trigger):
    if not trigger.group(2):
        bot.reply(u'\[T]/ \[T]/')
    else:
        bot.say(u'{0}: \[T]/ \[T]/'.format(clean(trigger.group(2).strip())))
    if 'praise' not in stats:
        stats['praise'] = 0
    stats['praise'] += 1
    save()
    return

@commands('hf')
def five_command(bot, trigger):
    if not trigger.group(2):
        bot.reply(u'ヘ( ^o^)ノ＼(^_^ )')
    else:
        bot.say(u'{0}: ヘ( ^o^)ノ＼(^_^ )'.format(clean(trigger.group(2).strip())))
    if 'hf' not in stats:
        stats['hf'] = 0
    stats['hf'] += 1
    save()
    return

@commands('eldritchstare')
def eld_stare_command(bot, trigger):
    if not trigger.group(2):
        bot.reply(u'ꙮ_ꙮ')
    else:
        bot.say(u'{0}: ꙮ_ꙮ'.format(clean(trigger.group(2).strip())))
    if 'eldritchstare' not in stats:
        stats['eldritchstare'] = 0
    stats['eldritchstare'] += 1
    save()
    return

taunts = ["Haw haw!",
          "Wololo.",
          "All hail, king of the losers!",
          "Sure, blame it on your ISP.",
          "My granny could scrap better than that.",
          "Ahh, you are such a fool.",
          "Not a wise decision, but a decision nonetheless."]

mp_taunts = ["I don't want to talk to you no more, you empty-headed animal food trough wiper!",
          "I fart in your general direction!",
          "Your mother was a hamster and your father smelt of elderberries!",
          "You don't frighten us, English pig-dogs!",
          "Go and boil your bottoms, you sons of a silly person!",
          "I blow my nose at you, so-called \"Arthur King,\" you and all your silly English Kniggets!",
          "You don't frighten us with your silly knees-bent running around advancing behaviour!",
          "'Allo, daffy English kniggets and Monsieur Arthur-King, who has the brain of a duck, you know!", 
          "I one more time-a unclog my nose in your direction, sons of a window-dresser!",
          "I wave my private parts at your aunties, you cheesy lot of second-hand electric donkey-bottom biters!",
          "I burst my pimples at you and call your door opening request a silly thing!",
          "You tiny-brained wipers of other people's bottoms!",
          "Yes, depart a lot at this time and cut the approaching any more or we fire arrows at the tops of your heads and make castanets out of your testicles already! Ha ha!",
          "And now remain gone, illegitimate faced buggerfolk!",
          "Daffy English kniggets! Thpppt!"]

continues = ["And, if you think you got nasty taunting this time, you ain't heard nothing yet!",
             "Now go away or I shall taunt you a second time-a!"]

@commands('taunt')
@commands('insult')
def taunt_command(bot, trigger):
    if randint(0,4) == 0:
        taunt = choice(taunts)
        followup = 0
    else:
        taunt = choice(mp_taunts)
        followup = randint(0,1)

    if not trigger.group(2):
        bot.reply(taunt)
        if followup == 1:
            bot.reply(choice(continues))
    else:
        bot.say("{0}: {1}".format(clean(trigger.group(2).strip()), taunt))
        if followup == 1:
            bot.say("{0}: {1}".format(clean(trigger.group(2).strip()), choice(continues)))
    
    stats['taunt'] += 1
    save()
    return
