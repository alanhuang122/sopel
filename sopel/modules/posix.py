# 2016.12.24 03:32:20 CST
#Embedded file name: modules/posix.py
from sopel.module import commands
import requests
from bs4 import BeautifulSoup as Soup

@commands('posix')
def posix_command(bot, trigger):
    """Is it POSIX?"""
    if not trigger.group(2):
        bot.say("THAT'S NOT POSIX")
    else:
        bot.say("{0}: YOU'RE NOT POSIX".format(trigger.group(2)))

@commands('man')
def man_command(bot, trigger):
    url = 'https://man.voidlinux.org/' + trigger.group(2)
    r = requests.get(url)
    if 'text/html' not in r.headers['Content-Type']:
        bot.say("THAT'S NOT POSIX^WHTML")
        return
    if r.status_code == 200:
        if 'No results found' in r.text:
            bot.say('No results found.')
            return
        s = Soup(r.text, 'lxml')
        try:
            bot.say('{} - {}'.format(s.body.div.contents[2].strip(), url))
        except AttributeError:
            bot.say(url)
    else:
        bot.say('Got {} return code when accessing {}'.format(r.status_code, url))
