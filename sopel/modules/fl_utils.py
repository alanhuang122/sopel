# 2016.12.24 03:31:56 CST
#Embedded file name: modules/profiles.py
from sopel.module import commands, example
from fuzzywuzzy import process
import re
import requests
import json
from sopel.modules import fl
from requests.utils import quote

storylets = [15691, 18728, 18730, 18729]
areas = ['Spite', 'Ladybones Road', 'Watchmaker\'s Hill', 'Veilgarden'] # Threshold is 60
items = {}
abb = {}

def load():
    data = {}
    try:
        with open('/home/alan/failbetter/fl-utils/utils/text/fl.dat') as f:
            last_seq = int(f.readline())
            for line in f:
                temp = json.loads(line)
                data[temp['key']] = temp['value']
        return data
    except Exception as e:
        print(e)
        return None

def render_events(ed):
    strings = []
    try:
        se = ed['SuccessEvent']
        strings.append('Success: {}'.format(se.list_effects()))
    except KeyError:
        pass
    try:
        rse = ed['RareSuccessEvent']
        strings.append('Rare Success ({}% chance): {}'.format(ed['RareSuccessEventChance'], rse.list_effects()))
    except KeyError:
        pass
    try:
        fe = ed['DefaultEvent']
        strings.append('{}{}'.format('Failure: ' if len(strings) > 0 else '', fe.list_effects()))
    except KeyError:
        pass
    try:
        rfe = ed['RareDefaultEvent']
        strings.append('Rare {}: ({}% chance): {}'.format('Failure' if len(strings) > 1 else 'Success', ed['RareDefaultEventChance'], rfe.list_effects()))
    except KeyError:
        pass
    return ' | '.join(strings)

#UB: list of materials or categories; can hook in with acr; print rare successes too
#list per location
def setup(bot):
    global storylets
    # initialize data
    data = load()
    fl.data = data
    storylets = [fl.Storylet.get(x) for x in storylets]

    # configure storylet references
    for storylet in storylets:
        for branch in storylet.branches:
            for event in branch.events:
                if event.endswith('Chance'):
                    continue
                for effect in branch.events[event].effects:
                    if effect.quality.nature == 1:
                        continue
                    try:
                        if effect.amount < 0:
                            continue
                    except TypeError:
                        if effect.amount.strip().startswith('-'):
                            continue
                    items[effect.quality.name] = branch

    global areas
    areas = {area: storylet for area, storylet in zip(areas, storylets)}

    for item in items:
        abb[''.join([word[0] for word in re.split(r'[ -]+', item)]).lower()] = item
        abb[''.join([word[0] for word in re.split(r'[ -]+', item) if word[0].isupper()]).lower()] = item

def render_html(string):
    string = re.sub(r'<.{,2}?br.{,2}?>','\n', string)
    string = re.sub(r'<.{,2}?p.{,2}?>','', string)
    string = re.sub(r'(?i)</?(em|i)>', '_', string)
    string = re.sub(r'(?i)</?(strong|b)>', '*', string)
    string = re.sub('\r\n', ' ', string)
    return string

@commands('code')
def code_command(bot, trigger):
    code = trigger.group(2).strip()
    r = requests.post(f'https://api.fallenlondon.com/api/accesscode/{code}').json()
    for key in fl.data:
        if key.startswith('accesscodes'):
            if fl.data[key].get('Name').lower() == code.lower():
                if fl.data[key].get('Tag') == 'Enigma' or 'Silver Tree' in fl.data[key].get('Tag'):
                    print(f'[fl-utils] Forbidden code {code} attempted')
                    bot.say(f'No data for code {code}.')
                    return
                else:
                    break

    if r['isSuccess']:
        code = r['accessCode']
        bot.say(f'Code {code["name"]}: {render_html(code["initialMessage"])} https://www.fallenlondon.com/a/{code["name"]}')
        bot.say(render_html(code['completedMessage']))
    else:
        bot.say(f'No data for code {code}.')

@commands('ub')
def ub_command(bot, trigger):
    if not trigger.group(2):
        bot.say('What Unfinished Business do you want information for?')
        return
    else:
        key = trigger.group(2).strip().lower()
        if key in abb:
            # Print one UB
            print_branch(bot, items[abb[key]])
            return
        match = process.extractOne(trigger.group(2), items.keys())
        if match[1] > 70:
            # print one UB
            print_branch(bot, items[match[0]])
            return
#        match = process.extractOne(trigger.group(2), areas)
#        if match[1] > 70:
#            # Print UBs in area
#            print_area(bot, areas[match[0]])
#            return
        bot.say('I couldn\'t understand that input.')

def print_branch(bot, branch):
    storylet = branch.parent
    bot.say('Storylet: {} | Branch: {} | {}'.format(storylet.title, branch.title, render_events(branch.events)))

@commands('level')
@example('.level 20 to 50')
def cp_command(bot, trigger):
    if not trigger.group(2):
        bot.say('Usage: .level [X to] Y')
        return
    match = re.findall(r'\d+', trigger.group(2))
    if re.search(r'-\d', trigger.group(2)):
        bot.say('Negative numbers are not allowed.')
        return
    if len(match) < 1:
        bot.say('No numbers found.')
        return
    elif len(match) == 1:
        other, main = calc_cp(int(match[0]))
        if other != main:
            bot.say('It takes {} cp ({} for Watchful/Dangerous/Shadowy/Persuasive) to go from level 0 to level {}'.format(other, main, match[0]))
        else:
            bot.say('It takes {} cp to go from level 0 to level {}'.format(main, match[0]))
    elif len(match) == 2:
        other, main = calc_cp(int(match[1]), int(match[0]))
        if other != main:
            bot.say('It takes {} cp ({} for Watchful/Dangerous/Shadowy/Persuasive), depending on current cp, to go from level {} to level {}'.format(other, main, match[0], match[1]))
        else:
            bot.say('It takes {} cp, depending on current cp, to go from level {} to level {}'.format(main, match[0], match[1]))
    elif len(match) > 2:
        bot.say('Only up to two numbers, please.')
        return

def calc_cp(upper, lower=0):
    if lower:
        upper_oth = (min(upper, 50) * (min(upper, 50) + 1) // 2) + (50 * (max(upper, 50) - 50))
        lower_oth = (min(lower, 50) * (min(lower, 50) + 1) // 2) + (50 * (max(lower, 50) - 50))
        upper_main = (min(upper, 70) * (min(upper, 70) + 1) // 2) + (70 * (max(upper, 70) - 70))
        lower_main = (min(lower, 70) * (min(lower, 70) + 1) // 2) + (70 * (max(lower, 70) - 70))
        return('{}-{}'.format(upper_oth - lower_oth - lower, upper_oth - lower_oth),
               '{}-{}'.format(upper_main - lower_main - lower, upper_main - lower_main))
    else:
        return ((min(upper, 50) * (min(upper, 50) + 1) // 2) + (50 * (max(upper, 50) - 50)),
                (min(upper, 70) * (min(upper, 70) + 1) // 2) + (70 * (max(upper, 70) - 70)))

def isint(string):
    try:
        _ = int(string)
        return True
    except ValueError:
        return False

@commands('cp')
@example('.cp 5 (plus/minus) 50')
def level_command(bot, trigger):
    if not trigger.group(2):
        bot.say('Usage: .cp [X <plus|minus>] Y')
        return

    parts = trigger.group(2).split()

    if len(parts) == 1:
        level = 0
        try:
            cp = int(parts[0])
        except ValueError:
            bot.say('{} is not an int'.format(parts[1]))
            return
        operation = add_cp
    elif len(parts) == 2 and all([isint(part) for part in parts]):
        level = int(parts[0])
        cp = int(parts[1])
        operation = sub_cp if cp < 0 else add_cp
        cp = abs(cp)
    elif len(parts) == 3:
        try:
            level = int(parts[0])
        except ValueError:
            bot.say('{} is not an int'.format(parts[0]))
            return
        try:
            cp = int(parts[2])
        except ValueError:
            bot.say('{} is not an int'.format(parts[2]))
            return

        if parts[1].lower() == 'plus' or parts[1] == '+':
            operation = add_cp
        elif parts[1].lower() == 'minus' or parts[1] == '-':
            operation = sub_cp
        else:
            bot.say('invalid operation {}'.format(parts[1]))
            return
    else:
        bot.say('No more than three tokens are allowed.')
        return

    if level < 0:
        bot.say('Negative levels are not allowed.')
        return

    lower = operation(level, cp, 50)
    upper = operation(level, cp, 70)

    if lower == upper or all([val[0] < 0 for val in lower + upper]):
        bot.say('Level {} {} {} cp results in {}'.format(level, '+' if operation == add_cp else '-', cp, format_levels(lower)))
    else:
        bot.say('Level {} {} {} cp results in {} ({} for Watchful/Dangerous/Shadowy/Persuasive)'.format(level, '+' if operation == add_cp else '-', cp, format_levels(lower), format_levels(upper)))

def format_levels(tup):
    if tup[0] == tup[1] or (tup[0][0] < 0 and tup[1][0] < 0):
        return format_level(tup[0])
    else:
        return 'anywhere from {} to {}'.format(format_level(tup[0]), format_level(tup[1]))

def format_level(tup):
    if tup[0] < 0:
        return "level 0"
    else:
        return "level {} + {} cp".format(tup[0], tup[1])

def add_cp(level, cp, const):
    extra = min(level, const-1)
    while cp >= min(level+1, const):
        level += 1
        cp -= min(level, const)
    lower = (level, cp)
    cp += extra
    while cp >= min(level+1, const):
        level += 1
        cp -= min(level, const)
    upper = (level, cp)
    return (lower, upper)

def sub_cp(level, cp, const):
    extra = min(level, const-1)
    cp_low = cp - extra
    level_low = level
    while cp_low >= min(level_low, const):
        cp_low -= min(level_low, const)
        level_low -= 1
        if level_low < 0:
            break
    if cp_low < 0:
        upper = (level_low, min(level_low-cp_low-extra, const-1))
    else:
        upper = (level_low-1, min(level_low-cp_low, const-1))
    while cp > min(level, const):
        cp -= min(level, const)
        level -= 1
        if level < 0:
            break
    lower = (level-1, min(min(level, const) - cp, const-1))
    return (lower, upper)

@commands('item')
def item_command(bot, trigger):
    if not trigger.group(2):
        bot.say(worker_command(trigger.nick, 1))
        return
    else:
        bot.say(worker_command(trigger.group(2), 1))
        return

@commands('quality')
def quality_command(bot, trigger):
    if not trigger.group(2):
        bot.say(worker_command(trigger.nick, 2))
        return
    else:
        bot.say(worker_command(trigger.group(2), 2))
        return

@commands('where')
def location_command(bot, trigger):
    if not trigger.group(2):
        bot.say(worker_command(trigger.nick, 3))
        return
    else:
        bot.say(worker_command(trigger.group(2), 3))
        return

@commands('profile')
def profile_command(bot, trigger):
    url = 'https://api.fallenlondon.com/api/profile'
    r = requests.get(url, params={'characterName': trigger.group(2).strip()})
    if r.status_code == 404:
        bot.say('Couldn\'t find that profile.')
        return
    data = json.loads(r.text)
    name = data.get('profileCharacter', {}).get('name')
    bot.say('https://www.fallenlondon.com/profile/{}'.format(quote(name)), alias=False)

def worker_command(user, index):
    url = 'https://api.fallenlondon.com/api/profile'
    r = requests.get(url, params={'characterName': user.strip()})
    if r.status_code == 404:
        return "I couldn't find that profile."
    else:
        data = json.loads(r.text)
        character = data['profileCharacter']
        if index is 1:
            return "{} has {}".format(character['name'], character['mantelpieceItem']['nameAndLevel'])
        elif index is 2:
            return "{} has {}".format(character['name'], character['scrapbookStatus']['nameAndLevel'])
        elif index is 3:
            if data['currentArea']['name'] == 'Your Lodgings':
                gender = data['characterName'].rsplit(None, 1)[1]
                if gender == "gentleman":
                    pronoun = "his"
                elif gender == "lady":
                    pronoun = "her"
                elif gender == "gender":
                    pronoun = "their"
                data['currentArea']['name'] = f'{pronoun} Lodgings'
            elif data['currentArea']['name'] == "a place you won't leave":
                gender = data['characterName'].rsplit(None, 1)[1]
                if gender == "gentleman":
                    pronoun = "he"
                elif gender == "lady":
                    pronoun = "she"
                elif gender == "gender":
                    pronoun = "they"
                data['currentArea']['name'] = f"a place {pronoun} won't leave"
            return f"{character['name']} is {'on' if 'Island' in data['currentArea']['name'] else 'in'} {data['currentArea']['name']}"

@commands('abom')
def abom_command(bot, trigger):
    string = worker_command('Darkroot', 2)
    bot.say(string[:string.rfind(':')] + ' 777' + string[string.rfind(':'):])

@commands('smen')
def smen_command(bot, trigger):
    bot.say(worker_command('Passionario', 2).rsplit(' ', 1)[0] + ' DAMNED.')

@commands('drugs')
def drugs_command(bot, trigger):
    bot.say('Call ' + worker_command('Call Now', 2).split(' ', 2)[2])

@commands('box')
def box_command(bot, trigger):
    bot.say(f"Gazzien {worker_command('Mr Forms', 1).split(' ', 2)[2].rsplit(' ', 4)[0]} Surprise Packages <3")
