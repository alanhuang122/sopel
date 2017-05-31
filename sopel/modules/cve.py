#!/usr/local/bin/python
#coding: latin-1

from sopel.module import commands, example, url
from bs4 import BeautifulSoup
import urllib2

@url('(^| )((http|https)://)?cve\.mitre\.org/cgi-bin/cvename.cgi\?name=(.+)')
def process_cve(bot, trigger, match):
    lookup(bot, match.group(0))

@commands('cve')
def cve_command(bot, trigger):
    """Look up a CVE by ID - CVE-YYYY-NNNN"""
    if trigger.group(2):
        lookup(bot, "https://cve.mitre.org/cgi-bin/cvename.cgi?name={0}".format(trigger.group(2)))

def lookup(bot, string):
    try:
        data = urllib2.urlopen(string)
    except urllib2.HTTPError:
        bot.say('404 - page not found')
        return
    soup = BeautifulSoup(data,"html.parser")
    if "ERROR" in soup.head.title.string:
        bot.say(soup.head.title.string)
        return
    tag = soup.find_all(string="Description")[0].parent.parent
    description = tag.next_sibling.next_sibling
    bot.say('{0} | {1}'.format(unicode(description.get_text().replace("\n"," ")),string))

