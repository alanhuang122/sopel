#!/usr/local/bin/python
#coding: latin-1

from sopel.module import commands, example, interval
import json, urllib2, time
from fuzzywuzzy import process
from collections import OrderedDict
import xml.etree.ElementTree as ET

@interval(10)
def update_news(bot):
    if not bot.config.news.target_channel:
        return
    timeofday = time.time()
    sec_12h = timeofday % 43200
    if not sec_12h < 10:
        return
    url = "https://newsapi.org/v1/articles?source=reuters&apiKey={0}".format(bot.config.news.key)
    response = urllib2.urlopen(url)
    data = json.load(response, object_pairs_hook=OrderedDict)

    if data['status'] is 'error':
        bot.say("Error: \"{0}\"".format(data['message']))
        return

    length_limit = 420
    headline_count = 0
    headlines = u""
    for key in data['articles']:
        if headline_count < 5:
            if len(headlines) + len(key['title']) + 2 > length_limit:
                break
            headlines += u"\"{0}\" {1} ".format(key['title'],bold('|'))
            headline_count += 1

    bot.say(u"It's {1}:00 CST. Latest headlines from Reuters: {0}".format(headlines[0:-3], time.localtime()[3]), bot.config.news.target_channel)
    bot.memory['news'] = data
    bot.memory['newssource'] = 'reuters'
    bot.memory['newsindex'] = headline_count

@commands('news')
@example('.news BBC')
def get_headlines(bot, trigger):
    """Grabs news headlines from various APIs and newsapi.org: .news <source> <number of headlines>
You can get more information about a headline with .news #"""
    try:
        index = int(trigger.group(2))
        if index < 1 or index > 20:
            bot.say("Ha ha, very funny.")
            return
        get_details(bot, index)
        return
    except (TypeError, ValueError):
        pass

    sources = {'AP' : 'associated-press',
               'Ars Technica' : 'ars-technica',
               'BBC' : 'bbc-news',
               'Bloomberg' : 'bloomberg',
               'CNN' : 'cnn',
               'Fox News' : 'fox', 
               'Hacker News' : 'hacker-news',
               'IGN' : 'ign', 
               'Newsweek' : 'newsweek', 
               'NPR' : 'npr', 
               'NY Times' : 'the-new-york-times',
               'Recode' : 'recode',  
               'Reuters' : 'reuters',
               'Sky News' : 'sky-news', 
               'The Guardian' : 'the-guardian-uk',
               'The Independent' : 'independent', 
               'The Next Web' : 'the-next-web', 
               'The Telegraph' : 'the-telegraph',
               'The Verge' : 'the-verge', 
               'TIME' : 'time', 
               'USA Today' : 'usa-today',
               'WSJ' : 'the-wall-street-journal'}

    names = {  'associated-press' : 'The Associated Press',
               'ars-technica' : 'Ars Technica',
               'bbc-news' : 'The BBC',
               'bloomberg' : 'Bloomberg News', 
               'cnn' : 'CNN',
               'fox' : 'Fox News', 
               'hacker-news' : 'Hacker News',
               'independent' : 'The Independent',
               'ign' : 'IGN', 
               'newsweek' : 'Newsweek', 
               'reuters' : 'Reuters',
               'recode' : 'Recode', 
               'sky-news' : 'Sky News', 
               'the-guardian-uk' : 'The Guardian (UK)',
               'the-new-york-times' : 'The New York Times',
               'the-next-web' : 'The Next Web', 
               'the-telegraph' : 'The Telegraph',
               'the-verge' : 'The Verge', 
               'the-wall-street-journal' : 'The Wall Street Journal',
               'time' : 'TIME Magazine',
               'usa-today' : 'USA Today'}
    if (not trigger.group(2)) or trigger.group(2) == "sources" or trigger.group(2) == "help":
        output = "My sources are: "
        for key in sorted(sources.keys()):
            output += key
            output += ", "
        bot.say(output[:-2])
        return
    sources.update({'Associated Press' : 'associated-press',
                    'Ars' : 'ars-technica',
                    'Bloomberg News' : 'bloomberg',
                    'Cable News Network' : 'cnn',
                    'National Public Radio' : 'npr',
                    'The New York Times' : 'the-new-york-times',
                    'TIME Magazine' : 'time',
                    'NYT' : 'the-new-york-times',
                    'The Wall Street Journal' : 'the-wall-street-journal'})
    params = trigger.group(2)

    try:
        number = int(params.rsplit(None,1)[-1]) #tries to parse last token of input as int
        if number < 1 or number > 20:
            bot.say("Ha ha, very funny.")
            number = 10
        elif number > 10:
            bot.say("I have an arbitrary limit of 10.")
        limit = True
    except ValueError:
        number = 5
        limit = False

    if limit:
        params = params.rsplit(None,1)[0]

    match = process.extractOne(params, sources.keys())
    if match[1] < 80:
        bot.say("I'm not sure I have that source. Closest match: {0} ({1}% confidence)".format(names[sources[match[0]]], match[1]))
        return
    elif match[1] < 90:
        bot.say("Not certain about source; using {0}".format(match[0]))

    if sources[match[0]] is 'npr':
        get_headlines_npr(bot, number)
        return
    if sources[match[0]] is 'fox':
        get_headlines_fox(bot, number)
        return
    
    url = "https://newsapi.org/v1/articles?source={0}&apiKey={1}".format(sources[match[0]], bot.config.news.key)
    response = urllib2.urlopen(url)
    data = json.load(response, object_pairs_hook=OrderedDict)
    
    if data['status'] is 'error':
        bot.say(u"Error: \"{0}\"".format(data['message']))
        return

    length_limit = 430 - len(names[sources[match[0]]])
    continuing = False
    headline_count = 0
    headlines = u''
    for key in data['articles']:
        if headline_count < number:
            if len(headlines) + len(key['title']) + 2 > length_limit and not continuing:
                bot.say(u"Latest headlines from {0}: {1}".format(names[sources[match[0]]], headlines[0:-2]))
                headlines = u''
                continuing = True
            elif len(headlines) + len(key['title']) + 2 > length_limit and continuing:
                bot.say(u"{0}".format(headlines[0:-4]))
                headlines = u''
            headlines += u"\"{0}\" {1} ".format(key['title'], bold('|'))
            headline_count += 1

    bot.say(u"{0}".format(headlines[0:-3]))

    bot.memory['news'] = data
    bot.memory['newssource'] = sources[match[0]]
    bot.memory['newsindex'] = headline_count
    return

def get_details(bot, index):
    if not bot.memory.contains('news'):
        bot.say("Where do you want headlines from?")
        return
    elif bot.memory['newsindex'] < index:
        bot.say("I don't have that headline.")
        return
    else:
        if bot.memory['newssource'] is 'npr':
            get_details_npr(bot, index)
            return
        if bot.memory['newssource'] is 'fox':
            get_details_fox(bot, index)
            return
        index = index - 1
        trimmed = False
        data = bot.memory['news']
        description = u''
        description += list(data['articles'])[index]['title'] + "\" - \"" +  list(data['articles'])[index]['description']
        url = list(data['articles'])[index]['url']
        req = urllib2.Request('https://www.googleapis.com/urlshortener/v1/url?key={0}&fields=id'.format(bot.config.google.api_key),'{{"longUrl": "{0}"}}'.format(url), {'Content-Type' : 'application/json'})
        data = urllib2.urlopen(req)
        response = json.load(data)
        url = response['id']
        limit = 470 #512 minus "PRIVMSG <target> :"
        while len(description) > (limit - len(url)):
            description = description.rsplit(None,1)[:-1]
            trimmed = True
        if trimmed:
            bot.say(u"\"{0}...\" {1}".format(description, url))
            return
        else:
            bot.say(u"\"{0}\" {1}".format(description, url))
            return

def get_headlines_npr(bot, count):
    url = "http://api.npr.org/query?id=1001&fields=title,teaser&dateType=story&sort=featured&output=JSON&apiKey={0}".format(bot.config.news.npr_key)
    response = urllib2.urlopen(url)
    data = json.load(response, object_pairs_hook=OrderedDict)
    data = data['list']['story']

    length_limit = 416
    headline_count = 0
    headlines = u""
    continuing = False
    for key in data:
        if headline_count < count:
            if len(headlines) + len(key['title']['$text']) + 2 > length_limit and not continuing:
                bot.say(u"Latest headlines from NPR: {0}".format(headlines[0:-2]))
                headlines = u''
                continuing = True
            elif len(headlines) + len(key['title']['$text']) + 2 > length_limit and continuing:
                bot.say(u"{0}".format(headlines[0:-2]))
                headlines = u''
            headlines += u"\"{0}\" {1} ".format(key['title']['$text'], bold('|'))
            headline_count += 1

    bot.say(u"{0}".format(headlines[0:-3]))

    bot.memory['news'] = data
    bot.memory['newssource'] = 'npr'
    bot.memory['newsindex'] = headline_count
    return



def get_details_npr(bot, index):
    index = index - 1
    trimmed = False
    data = bot.memory['news']
    description = data[index]['title']['$text'] + "\" - \"" + data[index]['teaser']['$text']
    url = data[index]['link'][2]['$text']
    limit = 470 #512 minus "PRIVMSG <target> :"
    req = urllib2.Request('https://www.googleapis.com/urlshortener/v1/url?key={0}&fields=id'.format(bot.config.google.api_key),'{{"longUrl": "{0}"}}'.format(url), {'Content-Type' : 'application/json'})
    data = urllib2.urlopen(req)
    response = json.load(data)
    url = response['id']
    while len(description) > (limit - len(url)):
        description = description.rsplit(None,1)[:-1]
        trimmed = True
    if trimmed:
        bot.say("\"{0}...\" {1}".format(description, url))
        return
    else:
        bot.say("\"{0}\" {1}".format(description, url))
        return

def get_headlines_fox(bot, count):
    url = 'http://feeds.foxnews.com/foxnews/latest?format=xml'
    response = urllib2.urlopen(url)
    tree = ET.parse(response)
    root = tree.getroot()
    
    length_limit = 410
    headline_count = 0
    headlines = u''
    iterator = root.iter('title')
    next(iterator)
    next(iterator)  #skip header information
    for article in iterator:
        if headline_count < count:
            if len(headlines) + len(article.text) + 2 > length_limit:
                break
            headlines += u'\"{0}\"; {1} '.format(article.text, bold('|'))
            headline_count += 1

    bot.say(u'Headlines from Fox News: {0}'.format(headlines[0:-3]))

    bot.memory['news'] = tree
    bot.memory['newssource'] = 'fox'
    bot.memory['newsindex'] = headline_count
    return

def get_details_fox(bot, index):
    tree = bot.memory['news']
    root = tree.getroot()
    article = root[0][11+index]
    bot.say("\"{0}\" Published {1} - {2} ".format(article[0].text, article[1].text, article[4].text))
    return
