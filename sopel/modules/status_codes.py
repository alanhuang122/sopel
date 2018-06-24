from sopel.module import commands
from http.client import responses

@commands('http')
def http_command(bot, trigger):
    try:
        code = int(trigger.group(2))
        bot.say('HTTP {}: {}'.format(code, responses[code]))
    except ValueError:
        bot.say('{} is not a valid number'.format(trigger.group(2)))
    except KeyError:
        bot.say('{} is not a valid HTTP status code'.format(trigger.group(2)))
