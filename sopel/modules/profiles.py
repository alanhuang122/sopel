# 2016.12.24 03:31:56 CST
#Embedded file name: modules/profiles.py
from sopel.module import commands, example
import requests, csv, urllib2
from requests.utils import quote
from bs4 import BeautifulSoup

def equal(a, b):
    try:
        return a.lower().replace(' ', '') == b.lower().replace(' ', '')
    except AttributeError:
        return a == b


@commands('item')
def item_command(bot, trigger):
    bot.say(worker_command(trigger.group(2), 1))


@commands('quality')
def quality_command(bot, trigger):
    bot.say(worker_command(trigger.group(2), 2))


def worker_command(user, index):
    url = quote('http://fallenlondon.storynexus.com/Profile/{0}'.format(user), safe=':/')
    data = requests.get(url)
    if data.history:
        return "I couldn't find that profile."
    else:
        soup = BeautifulSoup(data.text, 'html.parser')
        if index is 1:
            tag = soup.find('section', id='usersMantel')
        elif index is 2:
            tag = soup.find('section', id='usersScrapbook')
        text = tag.find_all('h1')[1]
        return u'{0} has {1}.'.format(soup.find('a', class_='character-name').text, text.text)


@commands('abom')
def abom_command(bot, trigger):
    string = worker_command('Darkroot', 2)
    bot.say(string[:string.rfind(':')] + ' 777' + string[string.rfind(':'):])


@commands('smen')
def smen_command(bot, trigger):
    bot.say(worker_command('Passionario', 2).rsplit(' ', 1)[0] + ' DAMNED.')


@commands('drugs')
def drugs_command(bot, trigger):
    bot.say('Call ' + worker_command('Call Now', 2).split(' ', 2)[2])


@commands('box')
def box_command(bot, trigger):
    bot.say('Gazzien ' + worker_command('Mr Forms', 1).split(' ', 2)[2].rsplit(' ', 4)[0] + ' Surprise Packages <3')
