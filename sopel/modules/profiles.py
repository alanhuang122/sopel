# 2016.12.24 03:31:56 CST
#Embedded file name: modules/profiles.py
from sopel.module import commands
import requests, re
from requests.utils import quote
from bs4 import BeautifulSoup

def equal(a, b):
    try:
        return a.lower().replace(' ', '') == b.lower().replace(' ', '')
    except AttributeError:
        return a == b


@commands('item')
def item_command(bot, trigger):
    if not trigger.group(2):
        bot.say(worker_command(trigger.nick, 1))
        return
    else:
        bot.say(worker_command(trigger.group(2), 1))
        return

@commands('quality')
def quality_command(bot, trigger):
    if not trigger.group(2):
        bot.say(worker_command(trigger.nick, 2))
        return
    else:
        bot.say(worker_command(trigger.group(2), 2))
        return

@commands('profile')
def profile_command(bot, trigger):
    url = quote('http://fallenlondon.storynexus.com/Profile/{0}'.format(trigger.group(2).strip()), safe=':/')
    data = requests.get(url)
    if data.history:
        bot.say('Couldn\'t find that profile.')
        return
    name = re.search(r'class="character-name">(.+?)</a>', data.text).group(1)
    bot.say(quote('http://fallenlondon.storynexus.com/Profile/{0}'.format(name), safe=':/'), alias=False)


def worker_command(user, index):
    url = quote('http://fallenlondon.storynexus.com/Profile/{0}'.format(user.strip()), safe=':/')
    data = requests.get(url)
    if data.history:
        return "I couldn't find that profile."
    else:
        soup = BeautifulSoup(data.text, 'lxml')
        if index is 1:
            tag = soup.find('section', id='usersMantel')
        elif index is 2:
            tag = soup.find('section', id='usersScrapbook')
        try:
            text = tag.find_all('h1')[1]
        except IndexError:
            return u'I couldn\'t find anything...'

        return u'{0} has {1}'.format(soup.find('a', class_='character-name').text, text.text)

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

@commands('ushabti')
def shabti_command(bot,trigger):
    bot.say('Vavakx ' + worker_command('Vavakx  Nonexus',1).split(' ',3)[3])
