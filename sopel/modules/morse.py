#!/usr/local/bin/python
#coding: latin-1

from sopel.module import commands

morse = {
        'A': '.-',     'B': '-...',   'C': '-.-.', 
        'D': '-..',    'E': '.',      'F': '..-.',
        'G': '--.',    'H': '....',   'I': '..',
        'J': '.---',   'K': '-.-',    'L': '.-..',
        'M': '--',     'N': '-.',     'O': '---',
        'P': '.--.',   'Q': '--.-',   'R': '.-.',
        'S': '...',    'T': '-',      'U': '..-',
        'V': '...-',   'W': '.--',    'X': '-..-',
        'Y': '-.--',   'Z': '--..',

        '0': '-----',  '1': '.----',  '2': '..---',
        '3': '...--',  '4': '....-',  '5': '.....',
        '6': '-....',  '7': '--...',  '8': '---..',
        '9': '----.',
        "." : ".-.-.-",
        "," : "--..--",
        ":" : "---...",
        ';' : '-.-.-.',
        "?" : "..--..",
        "'" : ".----.",
        "-" : "-....-",
        "/" : "-..-.",
        "@" : ".--.-.",
        "=" : "-...-",
        '+' : ".-.-.",
        "'" : ".----.",
        '!' : "-.-.--",
        '(' : '-.--.',
        ')' : '-.--.-',
        '&' : '.-...',
        '_' : '.-..-.',
        '$' : '...-..-'}

inverse = dict((v,k) for (k,v) in list(morse.items()))

@commands('encode')
def encode_command(bot, trigger):
    tokens = []
    not_found = []
    for char in trigger.group(2):
        if char is not ' ':
            if char.upper() in morse:
                tokens.append(morse[char.upper()])
            else:
                not_found.append(char)

    if len(not_found) is not 0:
        bot.say('Not found: {0}'.format(not_found))
    bot.say(' '.join(tokens))

@commands('decode')
def decode_command(bot, trigger):
    string = trigger.group(2).replace('_','-')
    string = string.split(None)
    msg = ''
    no_decode = []
    for char in string:
        if char in inverse:
            msg += inverse[char]
        elif char == '/':
            msg += ' '
        else:
            no_decode.append(char)

    if len(no_decode) is not 0:
        bot.say('Could not decode the following symbols: {0}'.format([str(x) for x in no_decode]))
    bot.say(msg)
