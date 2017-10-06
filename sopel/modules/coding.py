#!/usr/local/bin/python
#coding: latin-1

from sopel.module import commands
import base64

@commands('b64decode')
def b64d_command(bot, trigger):
    """Decode a base64 string"""
    if trigger.group(2):
        try:
            bot.reply(base64.b64decode(trigger.group(2)))
        except TypeError:
            bot.say('I couldn\'t decode that.')

@commands('b64encode')
def b64e_command(bot, trigger):
    """Encode a base64 string"""
    if trigger.group(2):
        bot.reply(base64.b64encode(trigger.group(2)))

@commands('b32decode')
def b32d_command(bot, trigger):
    """Decode a base32 string"""
    if trigger.group(2):
        try:
            bot.reply(base64.b32decode(trigger.group(2)))
        except TypeError:
            bot.say('I couldn\'t decode that.')

@commands('b32encode')
def b32e_command(bot, trigger):
    """Encode a base32 string"""
    if trigger.group(2):
        bot.reply(base64.b32encode(trigger.group(2)))

@commands('b16decode')
def b16d_command(bot, trigger):
    """Decode a base16 string"""
    if trigger.group(2):
        try:
            bot.reply(base64.b16decode(trigger.group(2)))
        except TypeError:
            bot.say('I couldn\'t decode that.')

@commands('b16encode')
def b16e_command(bot, trigger):
    """Encode a base16 string"""
    if trigger.group(2):
        bot.reply(base64.b16encode(trigger.group(2)))
