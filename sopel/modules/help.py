# coding=utf-8
"""
help.py - Sopel Help Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright © 2013, Elad Alfassa, <elad@fedoraproject.org>
Copyright © 2018, Adam Erdman, pandorah.org
Licensed under the Eiffel Forum License 2.

https://sopel.chat
"""


import textwrap
import collections
import requests
import pickle, os

from sopel.logger import get_logger
from sopel.module import commands, rule, example, priority

logger = get_logger(__name__)


def setup(bot):
    global help_prefix
    help_prefix = bot.config.core.help_prefix


@rule('$nick' '(?i)(help|doc) +([A-Za-z]+)(?:\?+)?$')
@example('.help tell')
@commands('help', 'commands')
@priority('low')
def help(bot, trigger):
    """Shows a command's documentation, and possibly an example."""
    if trigger.group(2):
        name = trigger.group(2)
        name = name.lower()

        # number of lines of help to show
        threshold = 3

        if name in bot.doc:
            if len(bot.doc[name][0]) + (1 if bot.doc[name][1] else 0) > threshold:
                if trigger.nick != trigger.sender:  # don't say that if asked in private
                    bot.reply('The documentation for this command is too long; I\'m sending it to you in a private message.')
                msgfun = lambda l: bot.msg(trigger.nick, l)
            else:
                msgfun = bot.reply

            for line in bot.doc[name][0]:
                msgfun(line)
            if bot.doc[name][1]:
                msgfun('e.g. ' + bot.doc[name][1])
        else:
            bot.say('I can\'t find that command.')
            return
    else:
        # This'll probably catch most cases, without having to spend the time
        # actually creating the list first. Maybe worth storing the link and a
        # heuristic in config, too, so it persists across restarts. Would need a
        # command to regenerate, too...
        if 'command-list' in bot.memory and bot.memory['command-list'][0] == len(bot.command_groups):
            url = bot.memory['command-list'][1]
        else:
            msgs = []

            name_length = max(6, max(len(k) for k in list(bot.command_groups.keys())))
                
            heading1 = 'Module Name'.upper().ljust(name_length)
            msg = heading1 + '  ' + "commands:"
            indent = ' ' * (name_length + 2)
            # Honestly not sure why this is a list here
            msgs.append('\n'.join(textwrap.wrap(msg, subsequent_indent=indent)))
            
            for category, cmds in list(collections.OrderedDict(sorted(bot.command_groups.items())).items()):
                category = category.upper().ljust(name_length)
                cmds = set(cmds)  # remove duplicates
                cmds = '  '.join(cmds)
                msg = category + '  ' + cmds
                indent = ' ' * (name_length + 2)
                # Honestly not sure why this is a list here
                msgs.append('\n'.join(textwrap.wrap(msg, subsequent_indent=indent)))

            docs = []
            if os.path.isfile('/home/alan/.sopel/{0}-docs'.format(bot.config.help.config)):
                docs = pickle.load(open('/home/alan/.sopel/{0}-docs'.format(bot.config.help.config),'rb'))
            
            if docs == msgs:
                url = pickle.load(open('/home/alan/.sopel/{0}-docs_url'.format(bot.config.help.config),'rb'))
            else:
                url = create_list(bot, '\n\n'.join(msgs))
            if not url:
                return
            bot.memory['command-list'] = (len(bot.command_groups), url)
            pickle.dump(msgs,open('/home/alan/.sopel/{0}-docs'.format(bot.config.help.config),'wb'))
            pickle.dump(url,open('/home/alan/.sopel/{0}-docs_url'.format(bot.config.help.config),'wb'))
        bot.say("I've posted a list of my commands at {} - You can see "
                "more info about some of these commands by doing .help "
                "<command> (e.g. .help time)".format(url))


def create_list(bot, msg):
    msg = 'Command listing for {}@{}\n\n'.format(bot.nick, bot.config.core.host) + msg
    payload = {"content": msg}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    try:
        result = requests.post('https://ptpb.pw/', json=payload, headers=headers)
    except requests.RequestException:
        bot.say("Sorry! Something went wrong.")
        logger.exception("Error posting commands")
        return
    result = result.json()
    if 'url' not in result:
        bot.say("Sorry! Something went wrong.")
        logger.error("Invalid result %s", result)
        return
    return result['url']


@rule('$nick' r'(?i)help(?:[?!]+)?$')
@priority('low')
def help2(bot, trigger):
    response = (
        "Hi, I'm a bot. Say {1}commands to me in private for a list "
        "of my commands, or see https://sopel.chat for more "
        "general details. My owner is {0}."
        .format(bot.config.core.owner, help_prefix))
    bot.reply(response)
