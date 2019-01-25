# coding=utf-8
"""
tld.py - Sopel TLD Module
Copyright 2009-10, Michael Yanovich, yanovich.net
Licensed under the Eiffel Forum License 2.

https://sopel.chat
"""

from bs4 import BeautifulSoup as Soup
from sopel.module import commands, example
import requests
import re

uri = 'https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains'

bad_cols = ['Restrictions', 'Notes']

def search_row(string, row, headers):
    parts = [t.text for t in row.find_all('td')]
    for x in range(min(len(headers), len(parts))):
        if headers[x] not in bad_cols:
            if string in parts[x]:
                return True
    return False

@commands('tld')
@example('.tld uk')
def get_tld(bot, trigger):
    tld = trigger.group(2)
    if tld[0] != '.' and not tld.startswith('xn--'):
        tld = '.{}'.format(tld)
    page = requests.get(uri)
    s = Soup(page.text, 'lxml')
    tables = s.find_all('table', class_='wikitable')
    for t in tables:
        if tld in str(t):
            table = t
            break
    if not table:
        bot.say('TLD {} not found')
        return
    title = table.find_previous_sibling(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']).text
    title = title[:-6].strip() # strip out [edit]
    headers = [t.text for t in table.tr.find_all('th')]
    rows = table.find_all('tr')
    for r in rows:
        if search_row(tld, r, headers):
            row = r
            break
    parts = [t.text for t in row.find_all('td')]
    headers = headers[:len(parts)]
    for x in range(len(headers)):
        if headers[x] in bad_cols:
            headers.append(headers[x])
            headers.remove(headers[x])
            parts.append(parts[x])
            parts.remove(parts[x])
            break
            # moving long columns to end of lists
            # there will only ever be one "bad column"
    strings = []
    for x in range(min(len(headers), len(parts))):
        if len(re.sub(r'\[.+?\]', '', parts[x])) > 1:
            strings.append('{}: {}'.format(headers[x], parts[x].strip()))
    string = re.sub(r'\[.+?\]', '', '{}: {}'.format(title, ' | '.join(strings)))
    string = re.sub('\n', ' ', string)
    bot.say(string)


#@commands('tld')
#@example('.tld ru')
def gettld(bot, trigger):
    """Show information about the given Top Level Domain."""
    page = requests.get(uri).text
    tld = trigger.group(2)
    if not tld:
        bot.reply("You must provide a top-level domain to search.")
        return  # Stop if no tld argument is provided
    if tld[0] == '.':
        tld = tld[1:]
    search = r'(?i)<td><a href="\S+" title="\S+">\.{0}</a></td>\n(<td><a href=".*</a></td>\n)?<td>([A-Za-z0-9].*?)</td>\n<td>(.*)</td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n'
    search = search.format(tld)
    re_country = re.compile(search)
    matches = re_country.findall(page)
    if not matches:
        search = r'(?i)<td><a href="\S+" title="(\S+)">\.{0}</a></td>\n<td><a href=".*">(.*)</a></td>\n<td>([A-Za-z0-9].*?)</td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n'
        search = search.format(tld)
        re_country = re.compile(search)
        matches = re_country.findall(page)
    if matches:
        matches = list(matches[0])
        i = 0
        while i < len(matches):
            matches[i] = r_tag.sub("", matches[i])
            i += 1
        desc = matches[2]
        if len(desc) > 400:
            desc = desc[:400] + "..."
        reply = "%s -- %s. IDN: %s, DNSSEC: %s" % (matches[1], desc,
                matches[3], matches[4])
        bot.reply(reply)
    else:
        search = r'<td><a href="\S+" title="\S+">.{0}</a></td>\n<td><span class="flagicon"><img.*?\">(.*?)</a></td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n'
        search = search.format(str(tld))
        re_country = re.compile(search)
        matches = re_country.findall(page)
        if matches:
            matches = matches[0]
            dict_val = dict()
            dict_val["country"], dict_val["expl"], dict_val["notes"], dict_val["idn"], dict_val["dnssec"], dict_val["sld"] = matches
            for key in dict_val:
                if dict_val[key] == "&#160;":
                    dict_val[key] = "N/A"
                dict_val[key] = r_tag.sub('', dict_val[key])
            if len(dict_val["notes"]) > 400:
                dict_val["notes"] = dict_val["notes"][:400] + "..."
            reply = "%s (%s, %s). IDN: %s, DNSSEC: %s, SLD: %s" % (dict_val["country"], dict_val["expl"], dict_val["notes"], dict_val["idn"], dict_val["dnssec"], dict_val["sld"])
        else:
            reply = "No matches found for TLD: {0}".format(str(tld))
        bot.reply(reply)
