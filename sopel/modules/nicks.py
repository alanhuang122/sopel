# 2016.12.24 03:31:41 CST
#Embedded file name: modules/nicks.py
from sopel.module import commands, example
import urllib2, csv

def equal(a, b):
    try:
        return a.lower().replace(' ', '') == b.lower().replace(' ', '')
    except AttributeError:
        return a == b


def chunkstring(string, length):
    return (string[0 + i:length + i] for i in range(0, len(string), length))


@commands('who', 'whois', 'username')
@example('.whois Alan')
def lookup_command(bot, trigger):
    """Returns the IGN of a user whose nick is in the pronoun sheet: https://goo.gl/q6CJQg"""
    url = 'http://docs.google.com/feeds/download/spreadsheets/Export?key=1l_fLXnNA-jeKFuh-o6wLBxNf_YX3Tyci-brqvkYSfaQ&exportFormat=csv'
    reader = csv.reader(urllib2.urlopen(url), dialect='excel')
    string = None
    for row in reader:
        if equal(trigger.group(2).strip(), row[0].strip()):
            string = row[2]
            break

    if not string:
        bot.say('Nick was not found in pronoun doc. https://goo.gl/q6CJQg')
        print trigger.group(2)
        return
    bot.say(string)
