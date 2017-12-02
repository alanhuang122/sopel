#!/usr/local/bin/python
from sopel.module import commands
import random, cPickle, requests, re
from requests.utils import quote

data = None

def setup(bot):
    global data
    try:
        data = cPickle.load(open('/home/alan/.sopel/cards.dat'))
    except:
        data = {'watchful': [], 'shadowy': [], 'dangerous': [], 'persuasive': []}

@commands('cards')
def cards_command(bot, trigger):
    '''Lists of Christmas Card recipients! Commands: .cards list [stat (optional)] [1-5 (optional)] - get names | .cards add <username> <stat> - add name to list | .cards del <username> <stat> - remove name from list | .cards find <username> - find all lists user is part of | Stats: [Watchful, Shadowy, Dangerous, Persuasive]'''
    if not trigger.group(2) or trigger.group(2).lower() == 'help':
        bot.say('Lists of Christmas Card recipients! Commands: .cards list [stat (optional)] [1-5 (optional)] - get names | .cards add <username> <stat> - add name to list | .cards del <username> <stat> - remove name from list | .cards find <username> - find all lists user is part of | Stats: [Watchful, Shadowy, Dangerous, Persuasive]')
        return
    global data
    try:
        cmd, params = trigger.group(2).strip().split(None, 1)
    except ValueError:
        cmd = trigger.group(2).strip()
        params = ''
    cmd = cmd.lower()
    if cmd == 'add':
        try:
            name, l = params.rsplit(None, 1)
        except ValueError:
            bot.say('Not enough parameters')
            return
        
        url = 'http://' + quote('fallenlondon.storynexus.com/Profile/{0}'.format(name))
        r = requests.get(url)
        if r.history:
            bot.say("Couldn't find user {0}.".format(name), alias=False)
            return
        name = re.search(r'class="character-name">(.+?)</a>', r.text).group(1)

        key = ''
        for k in data.keys():
            if k.startswith(l.lower()):
                key = k
                break
        
        if not key:
            bot.say("Invalid stat - choose 1 from [Watchful, Shadowy, Dangerous, Persuasive]")
            return
        
        if name.lower() in [x[1].lower() for x in data[key]]:
            bot.say('{} is already in list {}'.format(name, key.title()), alias=False)
            return

        data[key].append((trigger.nick, name))
        bot.say('Added user {} to list {}'.format(name, key.title()), alias=False)
        cPickle.dump(data, open('/home/alan/.sopel/cards.dat', 'w'))
        return

    elif cmd == 'del':
        try:
            name, l = params.rsplit(None, 1)
        except ValueError:
            bot.say('Not enough parameters')
            return
        
        key = ''
        for k in data.keys():
            if k.startswith(l.lower()):
                key = k
                break

        if not key:
            bot.say("Invalid stat - choose 1 from [Watchful, Shadowy, Dangerous, Persuasive]")
            return

        for x in xrange(len(data[key])):
            if data[key][x][1].lower() == name.lower():
                if trigger.nick.lower() == data[key][x][0]:
                    del data[key][x]
                    bot.say('Removed {} from list {}'.format(name, key.title()), alias=False)
                    cPickle.dump(data, open('/home/alan/.sopel/cards.dat', 'w'))
                    return
                else:
                    bot.say('Only {} can remove {} from the list'.format(data[key][x][0], data[key][x][1]), alias=False)
                    return

        bot.say('Could not find {} in list {}'.format(name, key.title()), alias=False)
        return
    
    elif cmd == 'list':
        parts = params.split(None)
        if len(parts) == 0:
            lists = []
            for key in data.keys():
                msg = get_list(key, 5)
                lists.append(msg)
            msg = ' | '.join(lists)
            bot.say(msg, alias=False)
        elif len(parts) == 1:
            key = ''
            for k in data.keys():
                if k.startswith(parts[0].lower()):
                    key = k
                    break
            if key:
                msg = get_list(key, 5)
                bot.say(msg, alias=False)
                return
            else:
                try:
                    limit = int(parts[0])
                    if limit < 1:
                        bot.say('Invalid limit')
                        return
                    if limit > 5:
                        limit = 5
                    lists = []
                    for key in data.keys():
                        msg = get_list(key, limit)
                        lists.append(msg)
                    msg = ' | '.join(lists)
                    bot.say(msg, alias=False)
                except:
                    bot.say("Invalid syntax - format is .cards list [stat (optional)] [1-5 (optional)]")
                    return
        elif len(parts) == 2:
            limit = int(parts[1])
            if limit < 1:
                bot.say('Invalid limit')
                return
            if limit > 5:
                limit = 5
            
            key = ''
            for k in data.keys():
                if k.startswith(parts[0].lower()):
                    key = k
                    break
            if key:
                msg = get_list(key, limit)
                bot.say(msg, alias=False)
                return
            else:
                bot.say("Invalid stat - choose 1 from [Watchful, Shadowy, Dangerous, Persuasive]")
                return
        else:
            bot.say('Too many parameters')
            return
    elif cmd == 'find':
        name = params.strip()
        if not name:
            bot.say('Who do you want to find?')
            return

        lists = []
        for i in data.items():
            for x in i[1]:
                if name.lower() == x[1].lower():
                    lists.append(i[0].title())
                    name = x[1]

        if not lists:
            bot.say('{} was not found in any lists'.format(name), alias=False)
            return
        else:
            bot.say('{} is in the following lists: {}'.format(name, ', '.join(lists)), alias=False)
            return
    elif cmd == 'clear' and trigger.owner:
        print('[cards] clearing cards')
        data = {'watchful': [], 'shadowy': [], 'dangerous': [], 'persuasive': []}
        cPickle.dump(data, open('/home/alan/.sopel/cards.dat', 'w'))
    elif cmd == 'dump' and trigger.owner:
        print('[cards] {}'.format(data))
    else:
        bot.say("I don't know what you want me to do.")

def get_list(key, limit):
    if len(data[key]) == 0:
        msg = '{}: [N/A]'.format(key.title())
    elif len(data[key]) < limit + 1:
        random.shuffle(data[key])
        msg = '{}: {}'.format(key.title(), '[{}]'.format(', '.join([x[1] for x in data[key]])))
    else:
        msg = '{}: {}'.format(key.title(), '[{}]'.format(', '.join([x[1] for x in random.sample(data[key], limit)])))
    return msg

