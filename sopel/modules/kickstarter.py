#!/usr/bin/python
#coding: utf-8

from sopel.module import commands
import requests, re
from bs4 import BeautifulSoup as Soup

url = 'https://www.kickstarter.com/projects/1144821177/cultist-simulator-behold-our-end'

@commands('ks')
def kickstarter_command(bot, trigger):
    r = requests.get(url)
    s = Soup(r.text, 'lxml')
    title = s.h2.text.strip()
    try:
        st = s.find_all('span', class_="inline-flex items-center ml2 tipsy_s")[0]['title']
        parts = re.findall('(\xa3.+?)[ <]', st)
    except:
        st = s.find_all('span', class_='block')
        parts = [st[0].text, st[1].span.text]
    num = float(parts[0][1:].replace(',',''))
    den = float(parts[1][1:].replace(',',''))
    percent = round(num*100/den, 2)
    bot.say(u'{} has earned {} out of its goal of {} ({}% funded)'.format(title, parts[0], parts[1], percent))
