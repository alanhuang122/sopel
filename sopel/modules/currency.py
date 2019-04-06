# coding=utf-8
# Copyright 2013 Elsie Powell, embolalia.com
# Licensed under the Eiffel Forum License 2

import re
import requests

from fuzzywuzzy import process
from sopel.module import commands, example, NOLIMIT

api_url = 'http://data.fixer.io/api/latest'
regex = re.compile(r'''
    (\d+(?:\.\d+)?)        # Decimal number
    \s*([a-zA-Z]{3})       # 3-letter currency code
    \s+(?:in|as|of|to)\s+  # preposition
    ([a-zA-Z]{3})          # 3-letter currency code
    ''', re.VERBOSE)

def setup(bot):
    global key
    global names
    global currencies
    key = bot.config.currency.api_key
    names = requests.get('http://data.fixer.io/api/symbols', params={'access_key': key}).json()['symbols']
    currencies = {v:k for k,v in names.items()}

def get_rate(bot, code):
    code = code.upper()
    if code == 'EUR':
        return 1, 'Euro'

    data = requests.get(api_url, params={'access_key': key, 'symbols': code}).json()
    if not data['success']:
        return None, None
    return 1 / data['rates'][code], names[code]

@commands('cur', 'currency', 'exchange')
@example('.cur 20 EUR in USD')
def exchange(bot, trigger):
    """Show the exchange rate between two currencies"""
    if not trigger.group(2):
        return bot.reply("No search term. An example: .cur 20 EUR in USD")
    match = regex.match(trigger.group(2))
    if not match:
        # It's apologetic, because it's using Canadian data.
        bot.reply("Sorry, I didn't understand the input.")
        return NOLIMIT

    amount, of, to = match.groups()
    try:
        amount = float(amount)
    except ValueError:
        bot.reply("Sorry, I didn't understand the input.")
    except OverflowError:
        bot.reply("Sorry, input amount was out of range.")
    display(bot, amount, of, to)


def display(bot, amount, of, to):
    if not amount:
        bot.reply("Zero is zero, no matter what country you're in.")
    of_rate, of_name = get_rate(bot, of)
    if not of_name:
        of_cur = process.extractOne(of, currencies.keys())
        print(of_cur)
        of_rate, of_name = get_rate(bot, of)
        if not of_name:
            bot.reply("Unknown currency: %s" % of)
            return
    to_rate, to_name = get_rate(bot, to)
    if not to_name:
        to_cur = process.extractOne(to, currencies.keys())
        print(to_cur)
        to_rate, to_name = get_rate(bot, to)
        if not to_name:
            bot.reply("Unknown currency: %s" % to)
            return

    print(amount, of_rate, to_rate)
    result = amount * of_rate / to_rate
    bot.say("{:.2f} {} ({}) = {:.2f} {} ({})".format(amount, of.upper(), of_name,
                                             result, to.upper(), to_name))
