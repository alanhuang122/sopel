#!/usr/local/bin/python
#coding: latin-1

from sopel.module import commands, example
import requests

@commands('cat')
def cat_command(bot, trigger):
    """Get a cat picture."""
    URL = "http://thecatapi.com/api/images/get?api_key=MTU0MDA0"
    count = 0
    while True:
        try:
            r = requests.get(URL)
            bot.say(r.url)
            break
        except requests.ConnectionError:
            if count > 5:
                bot.say("I'm having connection woes...")
                return
            count += 1
