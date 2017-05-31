# 2017.04.13 14:56:51 CDT
#Embedded file name: /usr/local/lib/python2.7/site-packages/sopel-6.4.0-py2.7.egg/sopel/modules/dice.py
u"""
dice.py - Dice Module
Copyright 2010-2013, Dimitri "Tyrope" Molenaars, TyRope.nl
Copyright 2013, Ari Koivula, <ari@koivu.la>
Licensed under the Eiffel Forum License 2.

http://sopel.chat/
"""
from __future__ import unicode_literals, absolute_import, print_function, division
import random
import re
import operator
import sopel.module
from sopel.tools.calculation import eval_equation

class DicePouch:

    def __init__(self, num_of_die, type_of_die, addition):
        u"""Initialize dice pouch and roll the dice.
        
        Args:
            num_of_die: number of dice in the pouch.
            type_of_die: how many faces the dice have.
            addition: how much is added to the result of the dice.
        """
        self.num = num_of_die
        self.type = type_of_die
        self.addition = addition
        self.dice = {}
        self.dropped = {}
        self.roll_dice()

    def roll_dice(self):
        u"""Roll all the dice in the pouch."""
        self.dice = {}
        self.dropped = {}
        for __ in range(self.num):
            number = random.randint(1, self.type)
            count = self.dice.setdefault(number, 0)
            self.dice[number] = count + 1

    def drop_lowest(self, n):
        u"""Drop n lowest dice from the result.
        
        Args:
            n: the number of dice to drop.
        """
        sorted_x = sorted(self.dice.items(), key=operator.itemgetter(0))
        for i, count in sorted_x:
            count = self.dice[i]
            if n == 0:
                break
            elif n < count:
                self.dice[i] = count - n
                self.dropped[i] = n
                break
            else:
                self.dice[i] = 0
                self.dropped[i] = count
                n = n - count

        for i, count in self.dropped.items():
            if self.dice[i] == 0:
                del self.dice[i]

    def get_simple_string(self):
        u"""Return the values of the dice like (2+2+2[+1+1])+1."""
        dice = self.dice.items()
        faces = (u'+'.join([str(face)] * times) for face, times in dice)
        dice_str = u'+'.join(faces)
        dropped_str = u''
        if self.dropped:
            dropped = self.dropped.items()
            dfaces = (u'+'.join([str(face)] * times) for face, times in dropped)
            dropped_str = u'[+%s]' % (u'+'.join(dfaces),)
        plus_str = u''
        if self.addition:
            plus_str = u'{:+d}'.format(self.addition)
        return u'(%s%s)%s' % (dice_str, dropped_str, plus_str)

    def get_compressed_string(self):
        u"""Return the values of the dice like (3x2[+2x1])+1."""
        dice = self.dice.items()
        faces = (u'%dx%d' % (times, face) for face, times in dice)
        dice_str = u'+'.join(faces)
        dropped_str = u''
        if self.dropped:
            dropped = self.dropped.items()
            dfaces = (u'%dx%d' % (times, face) for face, times in dropped)
            dropped_str = u'[+%s]' % (u'+'.join(dfaces),)
        plus_str = u''
        if self.addition:
            plus_str = u'{:+d}'.format(self.addition)
        return u'(%s%s)%s' % (dice_str, dropped_str, plus_str)

    def get_sum(self):
        u"""Get the sum of non-dropped dice and the addition."""
        result = self.addition
        for face, times in self.dice.items():
            result += face * times

        return result

    def get_number_of_faces(self):
        u"""Returns sum of different faces for dropped and not dropped dice
        
        This can be used to estimate, whether the result can be shown in
        compressed form in a reasonable amount of space.
        """
        return len(self.dice) + len(self.dropped)


def _roll_dice(bot, dice_expression):
    result = re.search(u'\n        (?P<dice_num>-?\\d*)\n        d\n        (?P<dice_type>-?\\d+)\n        (v(?P<drop_lowest>-?\\d+))?\n        $', dice_expression, re.IGNORECASE | re.VERBOSE)
    dice_num = int(result.group(u'dice_num') or 1)
    dice_type = int(result.group(u'dice_type'))
    if dice_type <= 0:
        bot.reply(u"I don't have any dice with %d sides. =(" % dice_type)
        return None
    if dice_num < 0:
        bot.reply(u"I'd rather not roll a negative amount of dice. =(")
        return None
    if dice_num > 1000:
        bot.reply(u'I only have 1000 dice. =(')
        return None
    dice = DicePouch(dice_num, dice_type, 0)
    if result.group(u'drop_lowest'):
        drop = int(result.group(u'drop_lowest'))
        if drop >= 0:
            dice.drop_lowest(drop)
        else:
            bot.reply(u"I can't drop the lowest %d dice. =(" % drop)
    return dice


@sopel.module.commands(u'roll')
@sopel.module.commands(u'dice')
@sopel.module.commands(u'd')
@sopel.module.priority(u'medium')
@sopel.module.example(u'.roll 3d1+1', u'You roll 3d1+1: (1+1+1)+1 = 4')
@sopel.module.example(u'.roll 3d1v2+1', u'You roll 3d1v2+1: (1[+1+1])+1 = 2')
@sopel.module.example(u'.roll 2d4', u'You roll 2d4: \\(\\d\\+\\d\\) = \\d', re=True)
@sopel.module.example(u'.roll 100d1', u'[^:]*: \\(100x1\\) = 100', re=True)
@sopel.module.example(u'.roll 1001d1', u'I only have 1000 dice. =(')
@sopel.module.example(u'.roll 1d1 + 1d1', u'You roll 1d1 + 1d1: (1) + (1) = 2')
@sopel.module.example(u'.roll 1d1+1d1', u'You roll 1d1+1d1: (1)+(1) = 2')
def roll(bot, trigger):
    u""".dice XdY[vZ][+N], rolls dice and reports the result.
    
    X is the number of dice. Y is the number of faces in the dice. Z is the
    number of lowest dice to be dropped from the result. N is the constant to
    be applied to the end result.
    """
    dice_regexp = u'-?\\d*[dD]-?\\d+(?:[vV]-?\\d+)?'
    if not trigger.group(2):
        return bot.reply(u'No dice to roll.')
    arg_str = trigger.group(2)
    dice_expressions = re.findall(dice_regexp, arg_str)
    arg_str = arg_str.replace(u'%', u'%%')
    arg_str = re.sub(dice_regexp, u'%s', arg_str)
    f = lambda dice_expr: _roll_dice(bot, dice_expr)
    dice = list(map(f, dice_expressions))
    if None in dice:
        return

    def _get_eval_str(dice):
        return u'(%d)' % (dice.get_sum(),)

    def _get_pretty_str(dice):
        if dice.num <= 10:
            return dice.get_simple_string()
        elif dice.get_number_of_faces() <= 10:
            return dice.get_compressed_string()
        else:
            return u'(...)'

    eval_str = arg_str % tuple(map(_get_eval_str, dice))
    pretty_str = arg_str % tuple(map(_get_pretty_str, dice))
    try:
        result = eval_equation(eval_str)
    except Exception as e:
        bot.reply(u'SyntaxError, eval(%s), %s' % (eval_str, e))
        return

    bot.reply(u'You roll %s: %s = %d' % (trigger.group(2), pretty_str, result))


@sopel.module.commands(u'choice')
@sopel.module.commands(u'ch')
@sopel.module.commands(u'choose')
@sopel.module.priority(u'medium')
def choose(bot, trigger):
    u"""
    .choice option1|option2|option3 - Makes a difficult choice easy.
    """
    if not trigger.group(2):
        return bot.reply(u"I'd choose an option, but you didn't give me any.")
    choices = [trigger.group(2)]
    for delim in u'|\\/,':
        choices = trigger.group(2).split(delim)
        if len(choices) > 1:
            break

    for show_delim in u',|/\\':
        if show_delim not in trigger.group(2):
            show_delim += u' '
            break

    pick = random.choice(choices)
    return bot.reply(u'Your options: %s. My choice: %s' % (show_delim.join(choices), pick))


if __name__ == u'__main__':
    from sopel.test_tools import run_example_tests
    run_example_tests(__file__)
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2017.04.13 14:56:51 CDT
