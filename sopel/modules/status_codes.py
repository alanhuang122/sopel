from sopel.module import commands
from sopel.trigger import PreTrigger
from http.client import responses

@commands('http')
def http_command(bot, trigger):
    if not trigger.group(2):
        bot.say('https://twitter.com/stevelosh/status/372740571749572610')
        parts = trigger.raw.split(None)
        parts = parts[:4]
        parts.append(':https://twitter.com/stevelosh/status/372740571749572610')
        string = ' '.join(parts)

        pt = PreTrigger(bot.nick, string)
        bot.dispatch(pt)
        return
    try:
        code = int(trigger.group(2))
        bot.say('HTTP {}: {}'.format(code, responses[code]))
    except ValueError:
        bot.say('{} is not a valid number'.format(trigger.group(2)))
    except KeyError:
        bot.say('{} is not a valid HTTP status code'.format(trigger.group(2)))
