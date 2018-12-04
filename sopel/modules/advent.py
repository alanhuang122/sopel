import arrow
import mwclient
import re, json, requests, threading
from time import sleep
from sopel.module import commands, rule, example, require_owner
from datetime import datetime

data = {}

codes = {}
cache = {}
start = None
end = None

def setup(bot):
    global codes
    global cache

    try:
        with open('/home/alan/.sopel/qualities.json') as f:
            for line in f:
                temp = json.loads(line)
                data[temp['key']] = temp['value']
    except:
        pass

    with open('/home/alan/.sopel/bare.json') as f:
        codes = json.loads(f.read())
    try:
        with open('/home/alan/.sopel/advent_cache.json', 'r') as f:
            cache = json.load(f)
    except IOError:
        cache = {}
        with open('/home/alan/.sopel/advent_cache.json', 'w') as f:
            json.dump({}, f)

    start_timer(bot)

def start_timer(bot):
    global start
    global end
    time = datetime.utcnow()
    # Is it not yet December?
    if time < datetime(time.year, 12, 1, 12):
        diff = datetime(time.year, 12, 1, 12) - time
    else:
        # Is it before noon?
        if time < datetime(time.year, 12, time.day, 12):
            diff = datetime(time.year, 12, time.day, 12) - time
        elif time > datetime(time.year, 12, 25, 12):
            diff = datetime(time.year + 1, 12, 1, 12) - time
        else:
            diff = datetime(time.year, 12, time.day + 1, 12) - time
    print(f'[advent] scheduling for {diff}')
    start = time
    end = time + diff
    timer = threading.Timer(diff.seconds, timed_advent, [bot, '#fallenlondon'])
    timer.start()

@commands('when')
def when_command(bot, trigger):
    diff = end - datetime.utcnow()
    bot.say('timer started {}, ending at {}, now {}, remaining {}'
            .format(start.strftime('%c'), 
                    end.strftime('%c'), 
                    datetime.utcnow().strftime('%c'), 
                    diff))
    return

@rule(r'^\.reloadcache$')
@require_owner()
def reload_cache(bot, trigger):
    global cache
    with open('/home/alan/.sopel/advent_cache.json', 'r') as f:
        cache = json.load(f)

@rule(r'^\.cache$')
@require_owner()
def print_cache(bot, trigger):
    print(cache)

@commands('updatecache')
def update_cache(bot, trigger):
    print(f'{trigger.nick} tried to update cache using {trigger.group(0)}')
    try:
        day, effects = trigger.group(2).split(None, 1)
        day = int(day)
    except:
        day = max([int(k) for k in cache])
        effects = trigger.group(2)

    cache[str(day)]['effects'] = effects
    with open('/home/alan/.sopel/advent_cache.json', 'w') as f:
        json.dump(cache, f)

@rule(r'^\.testadvent$')
@require_owner()
def testadvent(bot, trigger):
    timed_advent(bot)

def timed_advent(bot, channel):
    print('[advent] in timed_advent')
    global cache
    time = datetime.utcnow()
    day = time.day

    if day > 25:
        print('[advent] merry christmas; no more advent codes; rip timer')
        return

    print('[advent] looking for page')
    while True:
        sleep(1)
        try:
            advent = requests.get('https://api.fallenlondon.com/api/advent').json()
            current = advent.get('openableDoor')
            if current['releaseDay'] == day:
                break
        except:
            continue

    print('[advent] got page')
    code = current['accessCodeName']
    r = get_response(code)['accessCode']
    url = f'https://www.fallenlondon.com/a/{code}'
    effects = get_effects(code)
    if not effects:
        bot.say(f'Advent Day {day} - {code}: {render_html(r["initialMessage"])} {url}', channel)
        bot.say(f'{render_html(r["completedMessage"])} Effects: unknown', channel)
        cache[str(current['releaseDay'])] = {'name': code,
                                             'initial': r['initialMessage'],
                                             'url': url,
                                             'finished': r['completedMessage']}
    else:
        effect_text = str(effects)
        bot.say(f'Advent Day {day} - {code}: {render_html(r["initialMessage"])} {url}', channel)
        bot.say(f'{render_html(r["completedMessage"])} Effects: {effect_text}', channel)
        cache[str(current['releaseDay'])] = {'name': code,
                                             'initial': r['initialMessage'],
                                             'url': url,
                                             'finished': r['completedMessage'],
                                             'effects': effect_text}

    with open('/home/alan/.sopel/advent_cache.json', 'w') as f:
        json.dump(cache, f)

    # Make the wiki edit
    site = mwclient.Site('fallenlondon.fandom.com', path='/')
    site.login(bot.config.wikia.username, bot.config.wikia.password)
    page = site.pages['Advent Calendar 2018']
    text = page.text()
    today = arrow.get(datetime.now()).format('MMMM Do')
    if today not in page.text():
        edit = f"""\n\n=={today}==\n{url}\n\n[[File:{r['image']}small.png|left]] {r['initialMessage']}\n<br />\n\n'''Result:'''\n\n{r['completedMessage']}\n\n"""
        page.save(page.text() + edit, today)

    start_timer(bot)

@commands('advent')
@example('.advent 1')
def advent_command(bot, trigger):
    """Get advent calendar link."""
    time = datetime.utcnow()

    if time < datetime(time.year, 12, 1, 12):
        diff = datetime(time.year, 12, 1, 12) - time
        rem, seconds = divmod(diff.seconds, 60)
        hours, minutes = divmod(rem, 60)
        bot.say(f'No advent codes for another {diff.days} days, {hours} hours, {minutes} minutes, and {seconds} seconds.')
        return
            
    advent = requests.get('https://api.fallenlondon.com/api/advent').json()
    current = advent.get('openableDoor')

    try:
        expired_index = max([x['releaseDay'] for x in advent.get('expiredDoors')])
    except:
        expired_index = 0

    opened = advent.get('openedDoors')
    opened = {x['releaseDay']: x for x in opened}

    try:
        input = int(trigger.group(2))
    except ValueError:
        bot.say("That's not a number.")
        return
    except TypeError:
        input = 0
    
    # Handle negative number shorthand for past days
    if input < 0:
        if input < -25:
            bot.say('Be serious.')
            return
        else:
            day = time.day + input
            if time.hour < 12:
                day -= 1
            if day < 1:
                bot.say("I can't go that far back.")
                return
    elif input == 0:
        day = current['releaseDay']
    else: # input > 0
        if input > current['releaseDay']:
            if input > 31:
                bot.say('Be serious.')
            elif input > 25:
                bot.say('No advent codes after the 25th.')
            else:
                bot.say('Not released yet...')
            return
        day = input

    if day <= expired_index:
        try:
            entry = cache[str(day)]
        except KeyError:
            bot.say("I don't have any information for that day :<")
            return
        print('[advent] using cache for expired code')
        code = entry['name']

        r = get_response(code)

        if not r['isSuccess']:
            print('[advent] must use cache for all entry')
            bot.say(f'[EXPIRED] Advent Day {day} - {code}: {render_html(entry["initial"])}')
            try:
                bot.say(f'{render_html(entry["finished"])} Effects: {entry["effects"]}')
            except KeyError:
                bot.say(f'{render_html(entry["finished"])} Effects: unknown')
        else:
            r = r['accessCode']
            url = f'https://www.fallenlondon.com/a/{code}'
            bot.say(f'[EXPIRED] Advent Day {day} - {code}: {render_html(r["initialMessage"])} {url}')
            try:
                bot.say(f'{render_html(entry["finished"])} Effects: {entry["effects"]}')
            except KeyError:
                bot.say(f'{render_html(entry["finished"])} Effects: unknown')
            cache[str(day)] = {'name': code,
                               'initial': r['initialMessage'],
                               'url': url,
                               'finished': r['completedMessage'],
                               'effects': entry['effects']}

            if entry != cache[str(day)]:
                print('[advent] !!! updating cache with different information!')
                print(f'[advent] old was {entry}')
                print(f'[advent] new is {cache[str(day)]}')
                with open('/home/alan/.sopel/advent_cache.json', 'w') as f:
                    json.dump(cache, f)

    else:
        # Get the day's code
        if day == current['releaseDay']:
            code = current['accessCodeName']
        else:
            try:
                code = opened[day]['accessCodeName']
            except KeyError:
                bot.say('I was expecting that number to be an opened door, and it was not.')
                print(current)
                print(opened)

        # Get cache entry for the day - missing is ok
        try:
            entry = cache[str(day)]
        except KeyError:
            pass

        r = get_response(code)

        if r['isSuccess']:
            r = r['accessCode']
            url = f'https://www.fallenlondon.com/a/{code}'
            effects = get_effects(code)

            bot.say(f'Advent Day {day} - {code}: {render_html(r["initialMessage"])} {url}')

            if effects: # First try from known access codes
                bot.say(f'{render_html(r["completedMessage"])} Effects: {effects}')
            else:
                try:
                    bot.say(f'{render_html(r["completedMessage"])} Effects: {entry["effects"]}')
                except KeyError:
                    bot.say(f'{render_html(r["completedMessage"])} Effects: unknown')
                return  # If we pull from cache, don't update cache...

            # Update cache entry if necessary
            cache[str(day)] = {'name': code,
                               'initial': r['initialMessage'],
                               'finished': r['completedMessage'],
                               'effects': str(effects),
                               'url': url}

            if entry != cache[str(day)]:
                print('[advent] !!! updating cache with different information!')
                print(f'[advent] old was {entry}')
                print(f'[advent] new is {cache[str(day)]}')
                with open('/home/alan/.sopel/advent_cache.json', 'w') as f:
                    json.dump(cache, f)

        else:   # Did not get success from /api/accesscode
            try:
                print('[advent] !!! NOT isSuccess - must use cache')
                bot.say(f'Advent Day {day} - {code}: {render_html(entry["initial"])}')
                try:
                    bot.say(f'{render_html(entry["finished"])} Effects: {entry["effects"]}')
                except KeyError:
                    bot.say(f'{render_html(entry["finished"])} Effects: unknown')
            except:
                bot.say("I don't have any information for that day :<")

def get_response(code):
    return requests.post(f'https://api.fallenlondon.com/api/accesscode/{code}').json()

def get_effects(codename):
    cstring = codename.lstrip('0123456789')
    try:
        return [Effect(e) for e in codes[cstring]]
    except KeyError:
        return None

def render_html(string):
    string = re.sub(r'<.{,2}?br.{,2}?>','\n', string)
    string = re.sub(r'<.{,2}?p.{,2}?>','', string)
    string = re.sub(r'(?i)</?(em|i)>', '_', string)
    string = re.sub(r'(?i)</?(strong|b)>', '*', string)
    string = re.sub('\r\n', ' ', string)
    return string

class Quality:
    def __init__(self, jdata):
        #HimbleLevel is used to determine order within categories for items
        self.raw = jdata
        self.name = jdata.get('Name', '(no name)')
        self.id = jdata['Id']
        self.desc = jdata.get('Description', '(no description)')
        self.pyramid = 'UsePyramidNumbers' in jdata
        self.nature = jdata.get('Nature', 1) #1: quality; 2: item
        try:
            qldstr = jdata['ChangeDescriptionText']
            self.changedesc = parse_qlds(qldstr)
        except KeyError:
            self.changedesc = None
        try:
            qldstr = jdata['LevelDescriptionText']
            self.leveldesc = parse_qlds(qldstr)
        except KeyError:
            self.leveldesc = None
        try:
            variables = {}
            d = json.loads(jdata['VariableDescriptionText'])
            for x in list(d.items()):
                variables[x[0]] = parse_qlds(x[1])
            self.variables = variables
        except KeyError:
            self.variables = None
        self.cap = jdata.get('Cap')
        self.tag = jdata.get('Tag')
        self.test_type = 'Narrow' if 'DifficultyTestType' in jdata else 'Broad'
        self.difficulty = jdata.get('DifficultyScaler')
        self.slot = jdata.get('AssignToSlot', {}).get('Id')
        try:
            self.enhancements = []
            for x in jdata['Enhancements']:
                self.enhancements.append('{:+} {}'.format(x['Level'], Quality.get(x['AssociatedQuality']['Id']).name))
        except KeyError:
            pass

    def __repr__(self):
        return 'Quality: {}'.format(self.name)

    def __str__(self):
        string = 'Quality: {}'.format(self.name)
        try:
            string += '\nCategory: {}'.format(self.category)
        except AttributeError:
            pass
        try:
            if self.enhancements:
                string += '\nEnhancements: [{}]'.format(', '.join(self.enhancements))
        except AttributeError:
            pass
        return string

    @classmethod
    def get(self, id):
        key = 'qualities:{}'.format(id)
        return Quality(data[key])

    def get_changedesc(self, level):
        if self.changedesc and isinstance(level, int):
            descs = sorted(list(self.changedesc.items()), reverse=True)
            for x in descs:
                if x[0] <= level:
                    desc = x
                    break
                desc = (-1, 'no description')
            return desc
        return None

    def get_leveldesc(self, level):
        if self.leveldesc and isinstance(level, int):
            descs = sorted(list(self.leveldesc.items()), reverse=True)
            for x in descs:
                if x[0] <= level:
                    desc = x
                    break
                desc = (-1, 'no description')
            return desc
        return None

def sub_qualities(string):
    for x in re.findall(r'\[qb?:(\d+)\]', string):
        string = string.replace(x, Quality.get(int(x)).name)
    return string

def parse_qlds(string):
    qld = {}
    qlds = string.split('~')
    for d in qlds:
        level, text = d.split('|', 1)
        level = int(level)
        qld[level] = text
    return dict(sorted(qld.items()))

class Effect:   #done: Priority goes 3/2/1/0
    def __init__(self, jdata, costs=None):
        self.raw = jdata
        self.quality = Quality.get(jdata['AssociatedQuality']['Id'])
        self.equip = 'ForceEquip' in jdata
        try:
            self.amount = jdata['Level']
        except:
            try:
                self.amount = sub_qualities(jdata['ChangeByAdvanced']).strip()
            except KeyError:
                pass
        try:
            self.setTo = jdata['SetToExactly']
        except:
            try:
                self.setTo = sub_qualities(jdata['SetToExactlyAdvanced']).strip()
            except KeyError:
                pass
        try:
            self.ceil = jdata['OnlyIfNoMoreThan']
        except KeyError:
            pass
        try:
            self.floor = jdata['OnlyIfAtLeast']
        except KeyError:
            pass
        try:
            self.priority = jdata['Priority']
        except KeyError:
            self.priority = 0

    def __repr__(self):
        try:
            limits = ' if no more than {} and at least {}'.format(self.ceil, self.floor)
        except:
            try:
                limits = ' if no more than {}'.format(self.ceil)
            except:
                try:
                    limits = ' only if at least {}'.format(self.floor)
                except:
                    limits = ''
        if self.equip:
            limits += ' (force equipped)'

        try:
            if self.quality.changedesc and isinstance(self.setTo, int):
                desc = self.quality.get_changedesc(self.setTo)
                try:
                    return '{} (set to {} ({}){})'.format(self.quality.name, self.setTo, desc[1], limits)
                except TypeError:
                    pass
            return '{} (set to {}{})'.format(self.quality.name, self.setTo, limits)
        except:
            if self.quality.nature == 2 or not self.quality.pyramid:
                try:
                    return '{:+} x {}{}'.format(self.amount, self.quality.name, limits)
                except:
                    return '{} x {}{}'.format(('' if self.amount.startswith('-') else '+') + self.amount, self.quality.name, limits)
            else:
                try:
                    return '{} ({:+} cp{})'.format(self.quality.name, self.amount, limits)
                except:
                    return '{} ({} cp{})'.format(self.quality.name, ('' if self.amount.startswith('-') else '+') + self.amount, limits)
