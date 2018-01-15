#!/usr/local/bin/python
#coding: latin-1

from sopel.module import commands, example
from bs4 import BeautifulSoup
import urllib2

@commands('rfc')
@example('.rfc 1149')
def rfc_command(bot, trigger):
    """Look up a Request for Comments by number"""
    if trigger.group(2):
        URL = "https://tools.ietf.org/html/rfc{0}".format(trigger.group(2))
        try:
            data = urllib2.urlopen(URL)
        except urllib2.HTTPError:
            bot.say('404 - page not found')
            return
        soup = BeautifulSoup(data, 'lxml')
        title = soup.html.head.title.string

        bot.say('{0} | {1}'.format(title,URL))
