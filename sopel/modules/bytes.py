# coding=utf8
"""
bytes.py - Byte conversion module for Sopel
Copyright © 2015, Richard Petrie, <rap1011@ksu.edu>
Licensed Eiffel Forum License, version 2
"""

from sopel.module import commands, example, NOLIMIT
import re

ORDER_BYTES = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

FIND_INPUT = re.compile(r'(^\d*\.?\d+)\s*([bkmgtpezy]*)', re.IGNORECASE)


@commands('bytes')
@example('2048', '2048 B = 2 KB')
@example('160 KB', '163840 B = 160 KB = 0.156 MB')
@example('160 Kb', '20480 B = 20 KB')
@example('.5 MB', '524288 B = 512 KB = 0.5 MB')
def do_bytes(bot, trigger):
    """
    Handles input and 'says' the list of conversions
    """
    # Take and parse input
    if not trigger.group(2):
        bot.reply("Invalid or missing arguments")
        return NOLIMIT
    user_input = FIND_INPUT.match(trigger.group(2))
    if not user_input:
        bot.reply("Invalid or missing arguments")
        return NOLIMIT
    number = float(user_input.group(1))
    unit = user_input.group(2)

    # Handle bits
    if 'b' in unit and unit.upper() in ORDER_BYTES:
        number /= 8
        unit = unit.upper()

    # Validate input
    if not unit:
        unit = "B"
    if unit not in ORDER_BYTES:
        bot.reply("Invalid unit")
        return NOLIMIT

    bot.say(convert_bytes(number, unit))


def convert_bytes(num_bytes, sent_unit):
    """
    Does the conversion
    :param num_bytes: Number of bytes
    :param sent_unit: Unit given
    :return: A string with bytes and units
    """
    response = ''
    num_bytes *= (1024 ** ORDER_BYTES.index(sent_unit))
    for unit in ORDER_BYTES:
        size = num_bytes / (1024 ** ORDER_BYTES.index(unit))
        if size >= 0.01:
            response += ("{0:.3f} {1} = ".format(size, unit)).replace(".000", "")
    return response[:-2]  # Cut off last "= "
