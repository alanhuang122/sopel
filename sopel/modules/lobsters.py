from sopel.module import url
from bs4 import BeautifulSoup
import requests
from sopel.trigger import PreTrigger

@url('.*(https://lobste.rs/s/[^ ]+).*')
def lobsters_rule(bot, trigger, match):
    data = requests.get(f'{match.group(0)}.json').json()
    bot.say(f'[lobste.rs] {data["title"]} {data["url"]}')
#    parts = trigger.raw.split(None)
#    parts = parts[:4]
#    parts.append(f':{tag["href"]}')
#    string = ' '.join(parts)
#    print(string)

#    pt = PreTrigger(bot.nick, string)
#    bot.dispatch(pt)
