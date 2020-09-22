#!/usr/local/bin/python
#coding: latin-1

from sopel.module import commands
from lxml.html import fromstring
import random
import requests
import re

@commands('nf')
def cat_command(bot, trigger):
    """Get a quote from noobfarm.org."""
    if trigger.group(2):
        try:
            if (quote_number := int(trigger.group(2))):
                page = requests.get(f'https://noobfarm.org/quote/{quote_number}')
                if page.status_code != 200:
                    bot.say("Quote does not exist")
                    return
        except:
            bot.say("Invalid input")
            return
    else:
        main_page = requests.get('https://noobfarm.org')
        max_quote = re.search(r'<a href="/quote/(\d+)">', main_page.text).group(1)
        while True:
            quote_number = random.randint(1, int(max_quote))
            page = requests.get(f'https://noobfarm.org/quote/{quote_number}')
            if page.status_code == 200:
                break

    tree = fromstring(page.content)
    parts = [s.strip() for s in tree.xpath("//text()") if s.strip()]
    for x in range(len(parts)):
        if parts[x].startswith('Added: '):
            start = x
        elif parts[x].startswith('&copy Noobfarm'):
            end = x
    quote = '    '.join(parts[start+1:end])
    bot.say(f'[noobfarm] Quote #{quote_number}: {quote}')
