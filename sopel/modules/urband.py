from sopel.module import commands, example
import sopel
import requests
import json

@commands('ud')
@example('.ud word')
def urbandict(bot, trigger):
    """.ud <word> - Search Urban Dictionary for a definition."""

    word = trigger.group(2)
    if not word:
        return bot.say(urbandict.__doc__.strip())

    try:
        data = requests.get("http://api.urbandictionary.com/v0/define?term={0}".format(word))
        data = json.loads(data.text)
    except Exception, e:
        print(e)
        return bot.say("Error connecting to urban dictionary")
        
    if data['result_type'] == 'no_results':
        return bot.say("No results found for {0}".format(word))

    result = data['list'][0]
    url = 'http://www.urbandictionary.com/define.php?term={0}'.format(word)

    response = "{0} - {1}".format(result['definition'].strip()[:256], url)
    bot.say(response)
