# coding=utf-8
# Copyright 2010, Michael Yanovich (yanovich.net), and Morgan Goose
# Copyright 2012, Lior Ramati
# Copyright 2013, Elsie Powell (embolalia.com)
# Licensed under the Eiffel Forum License 2.
from __future__ import unicode_literals, absolute_import, print_function, division

import random, re, requests
from sopel.module import commands, url

def get_info(number=None):
    if number:
        url = 'http://xkcd.com/{}/info.0.json'.format(number)
    else:
        url = 'http://xkcd.com/info.0.json'
    data = requests.get(url).json()
    data['url'] = 'https://xkcd.com/' + str(data['num'])
    return data

def google(query, key):
    url = 'https://www.googleapis.com/customsearch/v1'
    data = requests.get(url, params={'key' : key, 'cx': '005137987755203522487:hytymhiw4na', 'q' : query}).json()
    if 'items' not in data:
        return None
    results = data['items']
    for result in results:
        match = re.match('(?:https?://)?xkcd.com/(\d+)/?', result['link'])
        if match:
            return match.group(1)
    return None

@commands('xkcd')
def xkcd(bot, trigger):
    """
    .xkcd - Finds an xkcd comic strip. Takes one of 3 inputs:
    If no input is provided it will return a random comic
    If numeric input is provided it will return that comic, or the nth-latest
    comic if the number is non-positive
    If non-numeric input is provided it will return the first google result for those keywords on the xkcd.com site
    """
    # get latest comic for rand function and numeric input
    latest = get_info()
    max_int = latest['num']

    # if no input is given (pre - lior's edits code)
    if not trigger.group(2):  # get rand comic
        random.seed()
        requested = get_info(random.randint(1, max_int + 1))
    else:
        query = trigger.group(2).strip()

        numbered = re.match(r"^(#|\+|-)?(\d+)$", query)
        if numbered:
            query = int(numbered.group(2))
            if numbered.group(1) == "-":
                query = -query
            return numbered_result(bot, query, latest)
        else:
            # Non-number: google.
            if (query.lower() == "latest" or query.lower() == "newest" or query.lower() == "today"):
                requested = latest
            else:
                number = google(query, bot.config.google.api_key)
                if not number:
                    bot.say('Could not find any comics for that query.')
                    return
                requested = get_info(number)

    say_result(bot, requested, True)


def numbered_result(bot, query, latest):
    max_int = latest['num']
    if query > max_int:
        bot.say(("Sorry, comic #{} hasn't been posted yet. "
                    "The last comic was #{}").format(query, max_int))
        return
    elif query <= -max_int:
        bot.say(("Sorry, but there were only {} comics "
                    "released yet so far").format(max_int))
        return
    elif abs(query) == 0:
        requested = latest
    elif query == 404 or max_int + query == 404:
        bot.say("404 - Not Found")  # don't error on that one
        return
    elif query > 0:
        requested = get_info(query)
    else:
        # Negative: go back that many from current
        requested = get_info(max_int + query)

    say_result(bot, requested)


def say_result(bot, result, say_link=True):
    if say_link:
        message = '{} | {} | Alt-text: {}'.format(result['url'], result['title'], result['alt'])
    else:
        message = '{} | Alt-text: {}'.format(result['title'], result['alt'])
    bot.say(message)


@url('(^| )((http|https)://)?(www\.)?xkcd.com/(\d+)')
def get_url(bot, trigger, match):
    latest = get_info()
    numbered_result(bot, int(match.group(5)), latest)
