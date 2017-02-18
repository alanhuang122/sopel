#!/usr/local/bin/python
#coding: latin-1

from sopel.module import commands, interval
from bs4 import BeautifulSoup
import urllib2

def setup(bot):
    data = urllib2.urlopen("https://www.kickstarter.com/projects/failbetter/sunless-skies-the-sequel-to-sunless-sea")
    soup = BeautifulSoup(data.read(), "html.parser")
    amount = soup.find_all('span', class_="inline-flex")[0]['title'].split(None)[2]
    amount = int(amount.replace(',','')[1:])
    backers = int(soup.find_all('div', id='backers_count')[0]['data-backers-count'])
    bot.memory['amount'] = amount
    bot.memory['backers'] = backers
    print('{} {}'.format(amount, backers))
    del data
    del soup
    return

@interval(300)
def poll(bot):
    data = urllib2.urlopen("https://www.kickstarter.com/projects/failbetter/sunless-skies-the-sequel-to-sunless-sea")
    soup = BeautifulSoup(data.read(), "html.parser")
    amount = soup.find_all('span', class_="inline-flex")[0]['title'].split(None)[2]
    backers = soup.find_all('div', id='backers_count')[0]['data-backers-count']
    backers = int(backers)
    number = amount.replace(',','')
    number = int(number[1:])
    del data
    del soup
    if bot.memory['amount'] < 270000:
        if number >= 270000:
            bot.say(u'Sunless Skies has raised {0} and unlocked the Inconvenient Aunt stretch goal! May God have mercy on our souls. https://goo.gl/NQywcT'.format(amount),'#fallenlondon')
            bot.memory['amount'] = number
    if bot.memory['backers'] < 8000:
        if backers >= 8000:
            bot.say(u'Sunless Skies has reached {0} backers and unlocked Portsmouth House! https://goo.gl/NQywcT'.format(backers),'#fallenlondon')
            bot.memory['backers'] = backers
    return

@commands('ks')
def ks_command(bot, trigger):
    """See how far along the SSk kickstarter is!"""

    data = urllib2.urlopen("https://www.kickstarter.com/projects/failbetter/sunless-skies-the-sequel-to-sunless-sea")
    soup = BeautifulSoup(data.read(), "html.parser")
    amount = soup.find_all('span', class_="inline-flex")[0]['title'].split(None)[2]
    backers = soup.find_all('div', id='backers_count')[0]['data-backers-count']
    bot.say(u'Sunless Skies has raised {0} from {1} backers! https://goo.gl/NQywcT'.format(amount, backers))
    del data
    del soup
    return
