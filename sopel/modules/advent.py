# 2016.12.24 03:29:00 CST
#Embedded file name: modules/advent.py
import re, json, requests, imp
from sopel.module import commands, example
from datetime import datetime
from base64 import b64decode
from Crypto.Cipher import AES

data = {}
codes = {}

def first(text,key):
    ecb = AES.new(key, AES.MODE_ECB)
    return ecb.decrypt(b64decode(text))[:16]

def second(text,key,iv):
    ecb = AES.new(key, AES.MODE_CBC, iv)
    return ecb.decrypt(b64decode(text))[16:].replace('\x0c','')

def decrypt(text):
    key = 'eyJUaXRsZSI6Ildo'
    iv = b64decode('7ENDyFzB5uxEtjFCpRpj3Q==')
    return first(text,key)+second(text,key,iv)

def get(id):
    data = requests.get('http://couchbase-fallenlondon.storynexus.com:4984/sync_gateway_json/{0}'.format(id), headers={'Host' : 'couchbase-fallenlondon.storynexus.com:4984', 'User-Agent' : None, 'Accept' : 'multipart/related,  application/json'}).json()
    return decrypt(data['body'])

def clean(s):
    temp = s.rsplit('}', 1)
    return '{}}}'.format(temp[0])

def acquire(id):
    print('acquiring {}'.format(id))
    return json.loads(unicode(clean(get(id)), 'utf-8'))

def update():
    global codes
    try:
        with open('/home/alan/fallenlondon/revs.json') as f:
            old = json.load(f)
    except:
        old = {}
    try:
        with open('/home/alan/fallenlondon/codes.json') as f:
            codes = json.load(f)
    except:
        codes = {}

    temp = requests.get('http://couchbase-fallenlondon.storynexus.com:4984/sync_gateway_json/_all_docs').json()
    revs = {}
    for value in temp['rows']:
        if 'accesscodes' in value['key']:
            revs[value['key']] = value['value']['rev']

    for row in revs.items():
        try:
            if old[row[0]] == row[1]:
                continue
            else:
                code = acquire(row[0])
                codes[code['Name'].lower()] = code
        except KeyError:
            code = acquire(row[0])
            codes[code['Name'].lower()] = code

    with open('/home/alan/fallenlondon/revs.json', 'w') as f:
        json.dump(revs, f)
    with open('/home/alan/fallenlondon/codes.json', 'w') as f:
        json.dump(codes, f)

def sub_qualities(string):
    for x in re.findall(r'\[q:(\d+)\]', string):
        string = string.replace(x, Quality(int(x)).name)
    return string

class Effect:
    def __init__(self, effect):
        self.raw = effect
        self.quality = Quality(effect['AssociatedQuality']['Id'])
        self.equip = u'ForceEquip' in effect
        try:
            self.amount = effect['Level']
        except:
            try:
                self.amount = sub_qualities(effect['ChangeByAdvanced'])
            except KeyError:
                pass
        try:
            self.setTo = effect['SetToExactly']
        except:
            try:
                self.setTo = sub_qualities(effect['SetToExactlyAdvanced'])
            except KeyError:
                pass
        try:
            self.ceil = effect['OnlyIfNoMoreThan']
        except KeyError:
            pass
        try:
            self.floor = effect['OnlyIfAtLeast']
        except KeyError:
            pass
        try:
            self.priority = effect['Priority']
        except KeyError:
            self.priority = 0
    def __repr__(self):
        try:
            limits = u' if no more than {} and at least {}'.format(self.ceil, self.floor)
        except:
            try:
                limits = u' if no more than {}'.format(self.ceil)
            except:
                try:
                    limits = u' only if at least {}'.format(self.floor)
                except:
                    limits = u''

        try:
            return u'{} (set to {}{})'.format(self.quality.name, self.setTo, limits)
        except:
            if self.quality.nature == 2 or not self.quality.pyramid:
                try:
                    return u'{:+} x {}{}'.format(self.amount, self.quality.name, limits)
                except:
                    return u'{} {}{}'.format('' if self.amount.startswith('-') else u'+' + self.amount, self.quality.name, limits)
            else:
                try:
                    return u'{} ({:+} cp{})'.format(self.quality.name, self.amount, limits)
                except:
                    return u'{} ({} cp{})'.format(self.quality.name, u'' if self.amount.startswith('-') else u'' + self.amount, limits)

class Quality:  #done
    def __init__(self, id):
        #HimbleLevel is used to determine order within categories for items
        jdata = data['qualities:{}'.format(id)]
        self.raw = jdata
        self.name = jdata['Name']
        self.id = id
        try:
            self.nature = jdata['Nature']
        except KeyError:
            self.nature = 1
        self.pyramid = u'UsePyramidNumbers' in jdata

class AccessCode:
    def __init__(self, jdata):
        self.raw = jdata
        try:
            self.name = jdata['Name']
        except:
            self.name = u'(no name)'
        try:
            self.message1 = jdata['InitialMessage']
        except:
            self.message1 = u'(no message)'
        try:
            self.message2 = jdata['CompletedMessage']
        except:
            self.message2 = u'(no message)'
        self.effects = []
        for e in jdata['QualitiesAffected']:
            self.effects.append(Effect(e))
    def __repr__(self):
        string = u'Access code name: {}'.format(self.name)
        string += u'\nInitial message: {}'.format(self.message1)
        string += u'\nFinish message: {}'.format(self.message2)
        string += u'\nEffects: {}'.format(self.list_effects())
        return string.encode('utf-8')
    def __unicode__(self):
        string = u'Access code name: {}'.format(self.name)
        string += u'\nInitial message: {}'.format(self.message1)
        string += u'\nFinish message: {}'.format(self.message2)
        string += u'\nEffects: {}'.format(self.list_effects())
        return string
    def list_effects(self):
        if self.effects != []:
            return u'[{}]'.format(u', '.join([unicode(e) for e in self.effects]))

def calculateTimeDiff():
    time = datetime.utcnow()
    if time.hour < 12:
        diff = time.replace(hour=12, minute=0, second=0, microsecond=0) - time
    else:
        diff = time.replace(day=time.day + 1, hour=12, minute=0, second=0, microsecond=0) - time
    return '{0}:{1:02d}:{2:02d}'.format(diff.seconds / 3600, diff.seconds / 60 % 60, diff.seconds % 60)

def setup(bot):
    update()
    global data
    data = json.load(open('/home/alan/fallenlondon/qualities.json'))

@commands('advent')
@example('.advent 1')
def advent_command(bot, trigger):
    """Get advent calendar link."""
    start = datetime.utcnow().replace(month=12,day=1,hour=12,minute=0,second=0,microsecond=0)
    now = datetime.utcnow()
    if now < start:
        diff = start-now
        bot.say('No advent codes for another {} days {} hours {:02d} minutes {:02d} seconds.'.format(diff.days, diff.seconds / 3600, diff.seconds / 60 % 60, diff.seconds % 60))
        return
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
        bot.say("I can't turn that into an integer.")
        return
    except TypeError:
        val = 0
    page = requests.get('http://fallenlondon.storynexus.com/advent')
    #page = requests.get('https://alanhuang.name/advent.html')
    current = json.loads(re.search('openableDoor ?= ?(.+?);', page.text).group(1))
    expired = json.loads(re.search('expiredDoors ?= ?(.+?);', page.text).group(1))
    opened = json.loads(re.search('openedDoors ?= ?(.+?);', page.text).group(1))
    futures = [x['ReleaseDay'] for x in json.loads(re.search('futureDoors ?= ?(.+?);', page.text).group(1))]

    if val > current['ReleaseDay']:
        if val > 25 and val < 32:
            bot.say('No advent codes after the 25th.')
        elif val < 26:
            bot.say('Not released yet...')
        else:
            bot.say("Ok, now you're just fucking with me.")
        return

    cache = json.load(open('/home/alan/.sopel/advent_cache.json'))
    codes = json.load(open('/home/alan/fallenlondon/codes.json'))

    if val == 0 or val == current['ReleaseDay'] or not trigger.group(2):
        # get latest code
        if day > 25:
            bot.say("No more advent codes. Will return in 2018!")
            return

        codename = current['AccessCodeName'].lower()
        url = 'http://fallenlondon.storynexus.com/a/{0}'.format(current['AccessCodeName'])
        req = requests.post('https://www.googleapis.com/urlshortener/v1/url?key={0}&fields=id'.format(bot.config.google.api_key), data=json.dumps({'longUrl': url}), headers={'Content-Type': 'application/json'})
        response = req.json()
        
        try:
            code = codes[codename]
        except KeyError:
            update()
            try:
                code = codes[codename]
            except KeyError:
                bot.say(u'Advent Day {0}: {1} {2}'.format(current['ReleaseDay'], get_snippet(url), response['id']))
                bot.say('Next code in {}'.format(calculateTimeDiff()))
                print('[advent|ERROR]: could not get code {}'.format(codename))
                return
        
        code = AccessCode(code)
        effects = code.list_effects()
        
        bot.say(u'Advent Day {0}: {1} {2}'.format(current['ReleaseDay'], code.message1, response['id']))
        bot.say(u'{} (Effects: {})'.format(code.message2, effects))
        bot.say('Next code in {}'.format(calculateTimeDiff()))
    
        cache[current['ReleaseDay']] = {'initial': code.message1, 'url': response['id'], 'finished': code.message2, 'effects': code.list_effects()}
        json.dump(cache, open('/home/alan/.sopel/advent_cache.json', 'w'))
        
        return

    for entry in expired:
        if entry['ReleaseDay'] == val:
            try:
                data = cache[str(val)]
            except KeyError:
                bot.say("I don't have any information for that day :<")
            print('[advent] using cache')
            bot.say(u'[EXPIRED] Advent Day {0}: {1} {2}'.format(val, data['initial'], data['url']))
            bot.say(u'{} (Effects: {})'.format(data['finished'], data['effects']))
            return

    for entry in opened:
        if entry['ReleaseDay'] == val:
            try:
                data = cache[str(val)]
            except KeyError:
                bot.say("I don't have any information for that day :<")
            print('[advent] using cache')
            bot.say(u'Advent Day {0}: {1} {2}'.format(val, data['initial'], data['url']))
            bot.say(u'{} (Effects: {})'.format(data['finished'], data['effects']))
            return

    bot.say("I couldn't find anything for day {0} :<".format(val))

def get_snippet(url):
    data = requests.get(url)
    lines = data.text.split('\n')
    lines = [l.strip() for l in lines if l.strip() != '']
    try:
        index = lines.index('<h3>Enter, Friend!</h3>')
    except ValueError:
        return None
    snippet = lines[index+1]
    snippet = re.sub('<.+?>','', snippet)
    return snippet
