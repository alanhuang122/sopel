# 2016.12.24 03:31:41 CST
#Embedded file name: modules/nicks.py
from sopel.module import commands, example
import requests

def equal(a, b):
    try:
        return a.lower().replace(' ', '') == b.lower().replace(' ', '')
    except AttributeError:
        return a == b

@commands('who', 'whois', 'username')
@example('.whois Alan')
def lookup_command(bot, trigger):
    """Returns the IGN of a user whose nick is in the pronoun sheet: https://goo.gl/q6CJQg"""
    if not trigger.group(2):
        bot.say('Pronoun doc: https://goo.gl/q6CJQg')
        return
    url = 'https://docs.google.com/feeds/download/spreadsheets/Export?key=1l_fLXnNA-jeKFuh-o6wLBxNf_YX3Tyci-brqvkYSfaQ&exportFormat=csv'
    reader = csv.reader(requests.get(url).text.split('\r\n'), dialect='excel')
    string = None
    for row in reader:
        if equal(trigger.group(2).strip(), row[0].strip()):
            string = row[2]
            break

    if not string:
        bot.say('Nick was not found in pronoun doc. https://goo.gl/q6CJQg')
        print(trigger.group(2))
        return
    bot.say(string)

#@commands('rwho')
def rwho_command(bot,trigger):
    """Returns the IGN of a user whose nick is in the pronoun sheet: https://goo.gl/q6CJQg"""
    url = 'https://docs.google.com/feeds/download/spreadsheets/Export?key=1l_fLXnNA-jeKFuh-o6wLBxNf_YX3Tyci-brqvkYSfaQ&exportFormat=csv'
    reader = csv.reader(requests.get(url).text.split('\r\n'), dialect='excel')
    string = None
    for row in reader:
        if trigger.group(2).strip().lower() in row[2].strip().lower():
            string = str(row)
            break

    if not string:
        bot.say('Nick was not found in pronoun doc. https://goo.gl/q6CJQg')
        print(trigger.group(2))
        return
    bot.say(string)
