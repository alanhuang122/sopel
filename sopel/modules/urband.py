from sopel.module import commands, example, url
import requests
import urllib.request, urllib.parse, urllib.error

@commands('ud')
@example('.ud word')
def ud_command(bot, trigger):
    """.ud <word> - Search Urban Dictionary for a definition."""

    word = trigger.group(2)
    if not word:
        return bot.say(urbandict.__doc__.strip())

    response = ud(word)
    if not response:
        bot.say("No results found for {0}".format(word))
        return
    bot.say(response)

def ud(word, say_url=True):
    try:
        data = requests.get("https://api.urbandictionary.com/v0/define?term={0}".format(word)).json()
    except Exception as e:
        print(('[urband] {}'.format(e)))
        return bot.say("Error connecting to urban dictionary")
        
    if not data['list']:
        return None

    result = data['list'][0]
    if say_url:
        url = 'https://www.urbandictionary.com/define.php?term={0}'.format(urllib.parse.quote_plus(word))
        response = "[Urban Dictionary] {0} - {1}".format(result['definition'].strip()[:256].replace('\n', ' '), url)
    else:
        response = "[Urban Dictionary] {0}".format(result['definition'].strip()[:256].replace('\n', ' '))
    return response

@url('(http(s?)://)?(www\.)?urbandictionary\.com/define\.php\?term=(.+)')
def get_ud(bot, trigger, match):
    term = match.group(4).split(None)[0]
    response = ud(term, say_url=False)
    if response:
        bot.say(response)
