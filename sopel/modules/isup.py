# coding=utf-8
"""Simple website status check with isup.me"""
# Author: Elsie Powell https://embolalia.com

import requests
from sopel.module import commands

from requests.exceptions import SSLError


@commands('isup', 'ping')
def isup(bot, trigger):
    """Checks if a website is up or down."""
    site = trigger.group(2)
    secure = trigger.group(1).lower() != 'isupinsecure'
    if not site:
        return bot.reply("What site do you want to check?")

    if site[:7] != 'http://' and site[:8] != 'https://':
        if '://' in site:
            protocol = site.split('://')[0] + '://'
            return bot.reply("Try it again without the %s" % protocol)
        else:
            site = 'http://' + site

    if not '.' in site:
        bot.say("I don't think that's a valid site.")
        return

    try:
        site = site.replace('http', 'https', 1)
        response = requests.get(site, allow_redirects=False)
    except requests.exceptions.SSLError:
        try:
            site = site.replace('https', 'http', 1)
            response = requests.get(site, allow_redirects=False)
        except Exception:
            bot.say(site + ' looks down from here.')
            return
    except Exception:
        bot.say(site + ' looks down from here.')
        return

    if response:
        bot.say(response.request.url + ' looks fine to me.')
    else:
        bot.say(site + ' is down from here.')
