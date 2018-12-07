import arrow
import mwclient
import re, json, requests, threading
import socket, ssl
from time import sleep
from sopel.module import commands, rule, example, require_owner
from datetime import datetime
from sopel.modules import fl

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
    timer = threading.Timer(diff.seconds - 5, timed_advent, [bot, '#fallenlondon'])
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
    timed_advent(bot, '#alantest')

def timed_advent(bot, channel):
    print('[advent] in timed_advent')
    global cache
    time = datetime.utcnow()
    day = time.day

    if day > 25:
        print('[advent] merry christmas; no more advent codes; rip timer')
        return

    while True:
        print('[advent] looking for page')
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
        bot.say(f'Advent Day {day} - {code}: {fl.render_html(r["initialMessage"])} {url}', channel)
        bot.say(f'{fl.render_html(r["completedMessage"])} Effects: unknown - please tell me using .updatecache [effects]', channel)
        cache[str(current['releaseDay'])] = {'name': code,
                                             'initial': r['initialMessage'],
                                             'url': url,
                                             'finished': r['completedMessage']}
    else:
        effect_text = str(effects)
        bot.say(f'Advent Day {day} - {code}: {fl.render_html(r["initialMessage"])} {url}', channel)
        bot.say(f'{fl.render_html(r["completedMessage"])} Effects: {effect_text}', channel)
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
        base_edit = f"""\n\n=={today}==\n{url}\n\n[[File:{r['image']}small.png|left]] {r['initialMessage']}\n<br />\n\n'''Result:'''\n\n{r['completedMessage']}\n\n"""
        if effects:
            modification = '\n'.join(generate_wiki_effects(effects)) + '\n\n'
            base_edit += modification
        page.save(page.text() + base_edit, today)

    send_advent(bot.config.discord.username, bot.config.discord.password, day, url)
    print('done with timed_advent')

    start_timer(bot)

def send_advent(user, pw, day, url):
    ctx = ssl.create_default_context()
    sock = ctx.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname='znc.alanhua.ng')
    sock.connect(('znc.alanhua.ng', 6667))
    sock.sendall(b'PASS ' + pw + b'\r\nNICK Alan\r\nUSER ' + user + b' 0 * :Alan\r\n')

    while True:
        data = sock.recv(4096)
        if not data:
            break
        if b'End of /NAMES list.\r\n' in data:
            break

    print('connected')
    sock.sendall(b'PRIVMSG #fl-sacksmas :day ' + str(day).encode('ascii') + b': ' + url.encode('ascii') + b'\r\n')

    sock.close()

def generate_wiki_effects(effects):
    template_list = []
    for effect in effects:
        quality_name = effect.quality.name
        try:
            limits = f', up to {effect.ceil+1} and if at least {effect.floor}'
        except:
            try:
                limits = f', up to {effect.ceil+1}'
            except:
                try:
                    limits = f', if at least {effect.floor}'
                except:
                    limits = ''
        try:
            if effect.setTo == 0:
                template_list.append(f'* {{{{Gone|{quality_name}}}}}')
            else:
                template_list.append(f'* {{{{Item Gain|{quality_name}|now={effect.setTo} x}}}}')
        except:
            if effect.quality.nature == 2 or not effect.quality.pyramid:
                try:
                    if effect.amount > 0:
                        template_list.append(f'* {{{{Item Gain|{quality_name}|{effect.amount} x}}}}' + (f' ({limits[2:]})' if limits else ''))
                    else:
                        template_list.append(f'* {{{{Item Loss|{quality_name}|{effect.amount} x}}}}' + (f' ({limits[2:]})' if limits else ''))
                except:
                    if effect.amount.startswith('-'):
                        template_list.append(f'* {{{{Item Loss|{quality_name}|{effect.amount} x}}}}' + (f' ({limits[2:]})' if limits else ''))
                    else:
                        template_list.append(f'* {{{{Item Gain|{quality_name}|{effect.amount} x}}}}' + (f' ({limits[2:]})' if limits else ''))
            else:
                try:
                    if effect.amount > 0:
                        template_list.append(f'* {{{{Increase|{quality_name}|+{effect.amount} CP{limits}}}}}')
                    else:
                        template_list.append(f'* {{{{Drop|{quality_name}|{effect.amount} CP{limits}}}}}')
                except:
                    if effect.amount.startswith('-'):
                        template_list.append(f'* {{{{Drop|{quality_name}|{effect.amount} CP{limits}}}}}')
                    else:
                        template_list.append(f'* {{{{Increase|{quality_name}|{effect.amount} CP{limits}}}}}')
    return template_list

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
            bot.say(f'[EXPIRED] Advent Day {day} - {code}: {fl.render_html(entry["initial"])}')
            try:
                bot.say(f'{fl.render_html(entry["finished"])} Effects: {entry["effects"]}')
            except KeyError:
                bot.say(f'{fl.render_html(entry["finished"])} Effects: unknown')
        else:
            r = r['accessCode']
            url = f'https://www.fallenlondon.com/a/{code}'
            bot.say(f'[EXPIRED] Advent Day {day} - {code}: {fl.render_html(r["initialMessage"])} {url}')
            try:
                bot.say(f'{fl.render_html(entry["finished"])} Effects: {entry["effects"]}')
            except KeyError:
                bot.say(f'{fl.render_html(entry["finished"])} Effects: unknown')
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

            bot.say(f'Advent Day {day} - {code}: {fl.render_html(r["initialMessage"])} {url}')

            if effects: # First try from known access codes
                bot.say(f'{fl.render_html(r["completedMessage"])} Effects: {effects}')
            else:
                try:
                    bot.say(f'{fl.render_html(r["completedMessage"])} Effects: {entry["effects"]}')
                except KeyError:
                    bot.say(f'{fl.render_html(r["completedMessage"])} Effects: unknown')
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
                bot.say(f'Advent Day {day} - {code}: {fl.render_html(entry["initial"])}')
                try:
                    bot.say(f'{fl.render_html(entry["finished"])} Effects: {entry["effects"]}')
                except KeyError:
                    bot.say(f'{fl.render_html(entry["finished"])} Effects: unknown')
            except:
                bot.say("I don't have any information for that day :<")

def get_response(code):
    return requests.post(f'https://api.fallenlondon.com/api/accesscode/{code}').json()

def get_effects(codename):
    cstring = codename.lstrip('0123456789')
    try:
        return [fl.Effect(e) for e in codes[cstring]]
    except KeyError:
        return None
