#!/usr/local/bin/python
#coding: latin-1

from sopel.module import commands
import random
import requests

@commands('cat')
def cat_command(bot, trigger):
    """Get a cat picture."""
    if random.randint(0,2) == 0:
        if random.randint(0,1) == 0:
            bot.say("meow~")
            return
        else:
            bot.say(":3c")
            return
    URL = "https://thecatapi.com/api/images/get?api_key=MTU0MDA0"
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
