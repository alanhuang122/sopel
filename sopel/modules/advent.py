# 2016.12.24 03:29:00 CST
#Embedded file name: modules/advent.py
import re, json, requests, string
from sopel.module import commands, example
from datetime import datetime
from itertools import cycle

def calculateTimeDiff():
    time = datetime.utcnow()
    if time.hour < 12:
        diff = time.replace(hour=12, minute=0, second=0, microsecond=0) - time
    else:
        diff = time.replace(day=time.day + 1, hour=12, minute=0, second=0, microsecond=0) - time
    return '{0}:{1:02d}:{2:02d}'.format(diff.seconds / 3600, diff.seconds / 60 % 60, diff.seconds % 60)

@commands('advent')
@example('.advent 1')
def advent_command(bot, trigger):
    """Get advent calendar link."""
    if datetime.utcnow().hour < 12:
        day = datetime.utcnow().day - 1
    else:
        day = datetime.utcnow().day
    try:
        val = int(trigger.group(2))
        if val < 0:
            val = day + val
            if val <= 0:
                bot.say("I can't go that far back.")
                return
    except ValueError:
        bot.say("I can't operate on that input. (error converting to int)")
        return
    except TypeError:
        val = 0

    if val > day:
        if val > 25:
            bot.say('No advent codes after the 25th.')
            return
        bot.say('Not released yet...')
        return
    with open('/home/alan/.sopel/advent') as page:
        li = page.readlines()
        running = True
        licycle = cycle(li)
        nextline = licycle.next()
        while running:
            thisline, nextline = nextline, licycle.next()
            openablePattern = re.compile('(?:var openableDoor = )(.+)(?:;)')
            match = openablePattern.search(nextline)
            if match:
                openable = json.loads(match.group(0).strip()[19:-1])
                opened = json.loads(licycle.next().strip()[18:-1])
                expired = json.loads(licycle.next().strip()[19:-1])
                break

    if val == 0 or val == day or not trigger.group(2):
        if day > 25:
            bot.say("No more advent codes. Will return in 2017!")
            return
        snippet = ''
        url = 'http://fallenlondon.storynexus.com/a/{0}'.format(openable['AccessCodeName'])
        data = urllib2.urlopen(url)
        li = data.readlines()
        running = True
        licycle = cycle(li)
        nextline = licycle.next()
        while running:
            thisline, nextline = nextline, licycle.next()
            if 'Enter, Friend!' in thisline:
                snippet = re.sub('<.+?>', '', string.strip(nextline))
                break

        req = urllib2.Request('https://www.googleapis.com/urlshortener/v1/url?key={0}&fields=id'.format(bot.config.youtube.api_key), '{{"longUrl": "{0}"}}'.format(url), {'Content-Type': 'application/json'})
        data = urllib2.urlopen(req)
        response = json.load(data)
        bot.say('Advent Day {0}: {1} {2}'.format(openable['ReleaseDay'], snippet, response['id']))
        return
    for entry in expired:
        if entry['ReleaseDay'] == val:
            bot.say('Advent Day {0} is EXPIRED.'.format(val))
            return

    for entry in opened:
        if entry['ReleaseDay'] == val:
            snippet = ''
            url = 'http://fallenlondon.storynexus.com/a/{0}'.format(entry['AccessCodeName'])
            data = urllib2.urlopen(url)
            li = data.readlines()
            running = True
            licycle = cycle(li)
            nextline = licycle.next()
            while running:
                thisline, nextline = nextline, licycle.next()
                if 'Enter, Friend!' in thisline:
                    print nextline
                    snippet = re.sub('<.+?>', '', string.strip(nextline))
                    break

            req = urllib2.Request('https://www.googleapis.com/urlshortener/v1/url?key={0}&fields=id'.format(bot.config.youtube.api_key), '{{"longUrl": "{0}"}}'.format(url), {'Content-Type': 'application/json'})
            data = urllib2.urlopen(req)
            response = json.load(data)
            bot.say('Advent Day {0}: {1} {2}'.format(entry['ReleaseDay'], snippet, response['id']))
            return

    bot.say("I couldn't find anything for day {0} :<".format(val))
