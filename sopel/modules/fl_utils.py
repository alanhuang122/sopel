# 2016.12.24 03:31:56 CST
#Embedded file name: modules/profiles.py
from sopel.module import commands, example
import requests, re
from requests.utils import quote
from bs4 import BeautifulSoup

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

@commands('profile')
def profile_command(bot, trigger):
    url = quote('http://fallenlondon.storynexus.com/Profile/{0}'.format(trigger.group(2).strip()), safe=':/')
    data = requests.get(url)
    if data.history:
        bot.say('Couldn\'t find that profile.')
        return
    name = re.search(r'class="character-name">(.+?)</a>', data.text).group(1)
    bot.say(quote('http://fallenlondon.storynexus.com/Profile/{0}'.format(name), safe=':/'), alias=False)


def worker_command(user, index):
    url = quote('http://fallenlondon.storynexus.com/Profile/{0}'.format(user.strip()), safe=':/')
    data = requests.get(url)
    if data.history:
        return "I couldn't find that profile."
    else:
        soup = BeautifulSoup(data.text, 'lxml')
        if index is 1:
            tag = soup.find('section', id='usersMantel')
        elif index is 2:
            tag = soup.find('section', id='usersScrapbook')
        try:
            text = tag.find_all('h1')[1]
        except IndexError:
            return 'I couldn\'t find anything...'

        return '{0} has {1}'.format(soup.find('a', class_='character-name').text, text.text)

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
    bot.say('Gazzien ' + worker_command('Mr Forms', 1).split(' ', 2)[2].rsplit(' ', 4)[0] + ' Surprise Packages <3')

@commands('ushabti')
def shabti_command(bot,trigger):
    bot.say('Vavakx ' + worker_command('Vavakx  Nonexus',1).split(' ',3)[3])
