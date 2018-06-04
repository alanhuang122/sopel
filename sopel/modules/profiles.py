# 2016.12.24 03:31:56 CST
#Embedded file name: modules/profiles.py
from sopel.module import commands
import requests, re
from requests.utils import quote

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
    url = 'https://api.fallenlondon.com/api/profile/{}'.format(quote(trigger.group(2).strip()))
    r = requests.get(url)
    data = r.json()
    if not data:
        bot.say('Couldn\'t find that profile.')
        return
    name = data.get('ProfileCharacter', {}).get('Name')
    if not name:
        bot.say('Couldn\'t find that profile.')
        return
    bot.say('https://beta.fallenlondon.com/profile/{}'.format(quote(name)), alias=False)

def worker_command(user, index):
    url = 'https://api.fallenlondon.com/api/profile/{}'.format(quote(user.strip()))
    r = requests.get(url)
    data = r.json()
    if not data:
        return "I couldn't find that profile."
    else:
        character = data['ProfileCharacter']
        if index is 1:
            return "{} has {}".format(character['Name'], character['MantelpieceItem']['NameAndLevel'])
        elif index is 2:
            return "{} has {}".format(character['Name'], character['ScrapbookStatus']['NameAndLevel'])
        elif index is 3:
            if 'your' in data['CurrentArea']['Name']:
                gender = data['CharacterName'].rsplit(None, 1)[1]
                if gender == "gentleman":
                    pronoun = "his"
                elif gender == "lady":
                    pronoun = "her"
                elif gender == "gender":
                    pronoun = "their"
                data['CurrentArea']['Name'] = '{} Lodgings'.format(pronoun)
            elif 'you' in data['CurrentArea']['Name']:
                gender = data['CharacterName'].rsplit(None, 1)[1]
                if gender == "gentleman":
                    pronoun = "he"
                elif gender == "lady":
                    pronoun = "she"
                elif gender == "gender":
                    pronoun = "they"
                data['CurrentArea']['Name'] = data['CurrentArea']['Name'].replace('you', pronoun)
            return "{} is in {}".format(character['Name'], data['CurrentArea']['Name'])

@commands('smen')
def smen_command(bot, trigger):
    bot.say(worker_command('Passionario', 2).rsplit(' ', 1)[0] + ' DAMNED.')

@commands('drugs')
def drugs_command(bot, trigger):
    bot.say('Call ' + worker_command('Call Now', 2).split(' ', 2)[2])
