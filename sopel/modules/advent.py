# 2016.12.24 03:29:00 CST
#Embedded file name: modules/advent.py
import re, json, requests, threading, cPickle
from time import sleep
from sopel.module import commands, rule, example, require_owner
from datetime import datetime
from base64 import b64decode
from Crypto.Cipher import AES
from HTMLParser import HTMLParser

data = {}
codes = {}
h = HTMLParser()
timer = None
start = None
end = None

def setup(bot):
    update()
    global data
    global codes
    data = cPickle.load(open('/home/alan/fl-utils/qualities.dat'))
    codes = cPickle.load(open('/home/alan/fl-utils/codes.dat'))
    time = datetime.utcnow()
    if time.hour < 12:
        diff = time.replace(hour=12, minute=0, second=0, microsecond=0) - time
    else:
        try:
            diff = time.replace(day=time.day + 1, hour=12, minute=0, second=0, microsecond=0) - time
        except:
            diff = time.replace(month=time.month+1, day=1, hour=12, minute=0, second=0, microsecond=0) - time
    print('[advent] scheduling for {0}:{1:02d}:{2:02d}'.format(diff.seconds / 3600, diff.seconds / 60 % 60, diff.seconds % 60))
    global start
    global end
    start = datetime.utcnow()
    end = datetime.utcnow() + diff
    global timer
    if timer:
        timer.cancel()
    timer = threading.Timer(diff.seconds, timed_advent, [bot])
    timer.start()

@commands('verify')
def verify_command(bot, trigger):
    if datetime.utcnow().hour < 12:
        day = datetime.utcnow().day - 1
    else:
        day = datetime.utcnow().day
    try:
        val = int(trigger.group(2))
        if val < 0:
            return
    except ValueError:
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
        return
    
    best = None

    if val == 0 or val == current['ReleaseDay'] or not trigger.group(2):
        # get latest code
        if day > 25:
            return

        codename = current['AccessCodeName'].lower()

        try:
            code = codes[codename]
            return
        except KeyError:
            update()
            try:
                code = codes[codename]
                return
            except KeyError:
                cstring = codename.lstrip('0123456789')
                for k in codes.keys():
                    if cstring in k:
                        year = int(re.match('[a-zA-Z_]+(\d+)_\d+[a-zA-Z]+', k).group(1))
                        if not best:
                            best = (year, k)
                        elif year > best[0]:
                            best = (year, k)

                if not best:
                    return
                else:
                    codes[codename] = codes[best[1]].copy()
                    codes[codename].pop('TimesUsed', None)
                    codes[codename].pop('ExpiresAt', None)
                    codes[codename]['Name'] = codename
                    codes[codename]['Id'] = 9999990 + current['ReleaseDay']
                    codes[codename]['Tag'] = 'ADVENT 2017 - Manual'
    '''    
    for entry in opened:
        if entry['ReleaseDay'] == val:
            codename = entry['AccessCodeName']
            try:
                code = codes[codename]
                return
            except KeyError:
                update()
                try:
                    code = codes[codename]
                    return
                except KeyError:
                    cstring = codename.lstrip('0123456789')
                    for k in codes.keys():
                        if cstring in k:
                            year = int(re.match('[a-zA-Z_]+(\d+)_\d+[a-zA-Z]+', k).group(1))
                            if not best:
                                best = (year, k)
                            elif year > best[0]:
                                best = (year, k)

                    if not best:
                        return
                    else:
                        codes[codename] = codes[best[1]].copy()
                        codes[codename].pop('TimesUsed', None)
                        codes[codename].pop('ExpiresAt', None)
                        codes[codename]['Name'] = codename
                        codes[codename]['Id'] = 9999990 + entry['ReleaseDay']
                        codes[codename]['Tag'] = 'ADVENT 2017 - Manual'
    '''
    with open('/home/alan/fl-utils/codes.dat', 'w') as f:
        cPickle.dump(codes, f)

@commands('when')
def when_command(bot, trigger):
    diff = end - datetime.utcnow()
    bot.say('timer started {}, ending at {}, now {}, remaining {}'
            .format(start.strftime('%c'), 
                    end.strftime('%c'), 
                    datetime.utcnow().strftime('%c'), 
                    '{0}:{1:02d}:{2:02d}'.format(diff.seconds / 3600, diff.seconds / 60 % 60, diff.seconds % 60)))
    return

@rule('^\.testadvent$')
@require_owner()
def testadvent(bot,trigger):
    timed_advent(bot)

def timed_advent(bot):
    global timer
    global start
    global end
    
    timer.cancel()
    time = datetime.utcnow()
    diff = time.replace(day=time.day + 1, hour=12, minute=0, second=0, microsecond=0) - time

    if time.month < 12:
        print('[advent] timer triggered but is not December yet - scheduling for {0}:{1:02d}:{2:02d}'.format(diff.seconds / 3600, diff.seconds / 60 % 60, diff.seconds % 60))
        start = time
        end = time + diff
        timer = threading.Timer(diff.seconds, timed_advent, [bot])
        timer.start()
        return

    day = time.day

    if day > 25:
        print('[advent] merry christmas; no more advent codes; rip timer')
        return
    try:
        cache = cPickle.load(open('/home/alan/.sopel/advent_cache.dat'))
    except IOError:
        cache = {}
        cPickle.dump({}, open('/home/alan/.sopel/advent_cache.dat', 'w'))

    print('[advent] looking for page')
    while True:
        sleep(1)
        try:
            page = requests.get('http://fallenlondon.storynexus.com/advent')
            current = json.loads(re.search('openableDoor ?= ?(.+?);', page.text).group(1))
            if current['ReleaseDay'] == day:
                break
        except:
            continue
    
    codename = current['AccessCodeName'].lower()
    url = 'http://fallenlondon.storynexus.com/a/{0}'.format(current['AccessCodeName'])
    req = requests.post('https://www.googleapis.com/urlshortener/v1/url?key={0}&fields=id'.format(bot.config.google.api_key), data=json.dumps({'longUrl': url}), headers={'Content-Type': 'application/json'})
    response = req.json()
    
    best = None

    try:
        code = codes[codename]
    except KeyError:
        update()
        try:
            code = codes[codename]
        except KeyError:
            cstring = codename.lstrip('0123456789')
            for k in codes.keys():
                if cstring in k:
                    year = int(re.match('[a-zA-Z_]+(\d+)_\d+[a-zA-Z]+', k).group(1))
                    if not best:
                        best = [year, k]
                    elif year > best[0]:
                        best = [year, k]

            if not best:
                bot.say(u'Advent Day {} - {}: {} {}'.format(current['ReleaseDay'], current['AccessCodeName'], render(get_snippet(url)), response['id']), '#fallenlondon')
                print('[advent|ERROR]: could not get code {}'.format(codename))
                return
            else:
                if best[0] == 0:
                    best[0] = "past year"
                elif best[0] == 2016:
                    best[0] = "last year"
                code = codes[best[1]]
                disclaimer = ' (note: effect from {}; may not be accurate)'.format(best[0])
    
    code = AccessCode(code)
    effects = code.list_effects()
    
    bot.say(u'Advent Day {} - {}: {} {}'.format(current['ReleaseDay'], current['AccessCodeName'], render(code.message1), response['id']), '#fallenlondon')
    bot.say(u'{} Effects: {}{}'.format(render(code.message2), effects, disclaimer if best else ''), '#fallenlondon')

    cache[current['ReleaseDay']] = {'name': current['AccessCodeName'], 'initial': code.message1, 'url': response['id'], 'finished': code.message2, 'effects': code.list_effects()}
    cPickle.dump(cache, open('/home/alan/.sopel/advent_cache.dat', 'w'))
    
    time = datetime.utcnow()
    diff = time.replace(day=time.day + 1, hour=12, minute=0, second=0, microsecond=0) - time

    print('[advent] scheduling for {0}:{1:02d}:{2:02d}'.format(diff.seconds / 3600, diff.seconds / 60 % 60, diff.seconds % 60))
    start = datetime.utcnow()
    end = datetime.utcnow() + diff
    timer = threading.Timer(diff.seconds, timed_advent, [bot])
    timer.start()

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
    start = datetime.utcnow().replace(month=12,day=1,hour=12,minute=0,second=0,microsecond=0)
    now = datetime.utcnow()
    if now < start:
        diff = start-now
        bot.say('No advent codes for another {} days, {} hours, {:02d} minutes, and {:02d} seconds.'.format(diff.days, diff.seconds / 3600, diff.seconds / 60 % 60, diff.seconds % 60))
        return
    if datetime.utcnow().hour < 12:
        day = datetime.utcnow().day - 1
    else:
        day = datetime.utcnow().day
    try:
        val = int(trigger.group(2))
        if val < -25:
            bot.say("Ok, now you're just fucking with me.")
            return
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

    try:
        if val > current['ReleaseDay']:
            if val > 25 and val < 32:
                bot.say('No advent codes after the 25th.')
            elif val < 26:
                bot.say('Not released yet...')
            else:
                bot.say("Ok, now you're just fucking with me.")
            return
    except TypeError:
        pass

    try:
        cache = cPickle.load(open('/home/alan/.sopel/advent_cache.dat'))
    except IOError:
        cache = {}
        cPickle.dump({}, open('/home/alan/.sopel/advent_cache.dat', 'w'))

    try:
        if not trigger.group(2) or val == 0 or val == current['ReleaseDay']:
            # get latest code
            if day > 25:
                bot.say("No more advent codes. Will return in 2018!")
                return

            codename = current['AccessCodeName'].lower()
            url = 'http://fallenlondon.storynexus.com/a/{0}'.format(current['AccessCodeName'])
            req = requests.post('https://www.googleapis.com/urlshortener/v1/url?key={0}&fields=id'.format(bot.config.google.api_key), data=json.dumps({'longUrl': url}), headers={'Content-Type': 'application/json'})
            response = req.json()
            
            best = None

            try:
                code = codes[codename]
            except KeyError:
                update()
                try:
                    code = codes[codename]
                except KeyError:
                    cstring = codename.lstrip('0123456789')
                    for k in codes.keys():
                        if cstring in k:
                            year = int(re.match('[a-zA-Z_]+(\d+)_\d+[a-zA-Z]+', k).group(1))
                            if not best:
                                best = [year, k]
                            elif year > best[0]:
                                best = [year, k]

                    if not best:
                        bot.say(u'Advent Day {0}: {1} {2}'.format(current['ReleaseDay'], render(get_snippet(url)), response['id']), '#fallenlondon')
                        print('[advent|ERROR]: could not get code {}'.format(codename))
                        return
                    else:
                        if best[0] == 0:
                            best[0] = "past year"
                        elif best[0] == 2016:
                            best[0] = "last year"
                        code = codes[best[1]]
                        disclaimer = ' (note: effect from {}; may not be accurate)'.format(best[0])
            
            code = AccessCode(code)
            effects = code.list_effects()
            
            bot.say(u'Advent Day {} - {}: {} {}'.format(current['ReleaseDay'], current['AccessCodeName'], render(code.message1), response['id']))
            bot.say(u'{} Effects: {}{}'.format(render(code.message2), effects, disclaimer if best else ''))
            bot.say('Next code in {}'.format(calculateTimeDiff()) if day < 25 else 'No more codes! Merry Christmas; see you in 2018!')
        
            cache[current['ReleaseDay']] = {'name': current['AccessCodeName'],'initial': code.message1, 'url': response['id'], 'finished': code.message2, 'effects': code.list_effects()}
            cPickle.dump(cache, open('/home/alan/.sopel/advent_cache.dat', 'w'))
        
            return
    except TypeError:
        pass

    for entry in expired:
        if entry['ReleaseDay'] == val:
            try:
                data = cache[val]
            except KeyError:
                bot.say("I don't have any information for that day :<")
            print('[advent] using cache')
            bot.say(u'[EXPIRED] Advent Day {} - {}: {}'.format(val, data['name'], render(data['initial'])))
            bot.say(u'{} Effects: {}'.format(render(data['finished']), data['effects']))
            return

    for entry in opened:
        if entry['ReleaseDay'] == val:
            try:
                data = cache[val]
            except KeyError:
                bot.say("I don't have any information for that day :<")
            print('[advent] using cache')
            bot.say(u'Advent Day {} - {}: {} {}'.format(val, data['name'], render(data['initial']), data['url']))
            bot.say(u'{} Effects: {}'.format(render(data['finished']), data['effects']))
            return

    bot.say("I couldn't find anything for day {0} :<".format(val))

@commands('code')
def code_command(bot, trigger):
    """Prints the result of an access code."""
    if not trigger.group(2):
        bot.say('Give me an access code.')
        return

    try:
        code = codes[trigger.group(2).lower()]
    except KeyError:
        update()
        try:
            code = codes[trigger.group(2).lower()]
        except KeyError:
            bot.say("I can't find that code.")
            return

    if code['Tag'] == 'Enigma':
        bot.say("I can't find that code.")
        return

    code = AccessCode(code)

    bot.say(u'Access code {}: {}'.format(render(code.name), render(code.message1)))
    bot.say(u'{} Effects: {}'.format(render(code.message2), code.list_effects()))

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

def update():
    global codes
    try:
        with open('/home/alan/fl-utils/revs.dat') as f:
            old = cPickle.load(f)
    except:
        old = {}
    try:
        with open('/home/alan/fl-utils/codes.dat') as f:
            codes = cPickle.load(f)
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

    with open('/home/alan/fl-utils/revs.dat', 'w') as f:
        cPickle.dump(revs, f)
    with open('/home/alan/fl-utils/codes.dat', 'w') as f:
        cPickle.dump(codes, f)

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
    print('[advent] acquiring {}'.format(id))
    return json.loads(unicode(clean(get(id)), 'utf-8'))

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
            self.message1 = h.unescape(jdata['InitialMessage'])
        except Exception as e:
            print e
            self.message1 = u'(no message)'
        try:
            self.message2 = h.unescape(jdata['CompletedMessage'])
        except Exception as e:
            print e
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

def render(string):
    string = re.sub(r'<.{,2}?br.{,2}?>',u' ', string)
    string = re.sub(r'<.{,2}?[pP].{,2}?>',u' ', string)
    string = string.replace('<em>', '\x1d')
    string = string.replace('<i>', '\x1d')
    string = string.replace('</em>', '\x1d')
    string = string.replace('</i>', '\x1d')
    string = string.replace('<strong>', '\x02')
    string = string.replace('</strong>', '*\x02')
    string = string.replace('<b>', '\x02')
    string = string.replace('</b>', '*\x02')
    return string
