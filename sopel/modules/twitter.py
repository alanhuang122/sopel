# coding=utf-8


from sopel import module
from sopel.config.types import StaticSection, ValidatedAttribute, NO_DEFAULT
from sopel.logger import get_logger

logger = get_logger(__name__)


class TwitterSection(StaticSection):
    consumer_key = ValidatedAttribute('consumer_key', default=NO_DEFAULT)
    consumer_secret = ValidatedAttribute('consumer_secret', default=NO_DEFAULT)


def configure(config):
    config.define_section('twitter', TwitterSection, validate=False)
    config.twitter.configure_setting(
        'consumer_key', 'Enter your Twitter consumer key')
    config.twitter.configure_setting(
        'consumer_secret', 'Enter your Twitter consumer secret')

client = None
import tweepy
def setup(bot):
    global client
    auth = tweepy.OAuthHandler(bot.config.twitter.consumer_key, bot.config.twitter.consumer_secret)
    auth.set_access_token(bot.config.twitter.auth_token, bot.config.twitter.auth_secret)
    client = tweepy.API(auth)

from sopel.tools.time import get_timezone, format_time
from html.parser import HTMLParser

h = HTMLParser()

@module.url('https?://(.+\.)?twitter.com/([^/]*)(?:/status/(\d+)).*')
def get_url(bot, trigger, match):
    global client
    tid = match.group(3)
    try:
        content = client.get_status(tid, tweet_mode='extended')
    except tweepy.TweepError as e:
        bot.say('{} error reaching the twitter API for {}'.format(e.message[0]['code'], match.group(0)))
        return
    
    content.full_text = h.unescape(content.full_text.replace('\n', ' '))
    if content.is_quote_status:
        content.quoted_status = client.get_status(content.quoted_status['id'], tweet_mode='extended')
        content.quoted_status.full_text = h.unescape(content.quoted_status.full_text.replace('\n', ' '))
    message = '[Twitter]'
    if content.is_quote_status:
        message += (' {content.quoted_status.user.name} '
                    '(@{content.quoted_status.user.screen_name}): '
                    '{content.quoted_status.full_text} | Quoted by').format(content=content)
        quote_id = content.quoted_status.id_str
        for url in content.entities['urls']:
            expanded_url = url['expanded_url']
            if expanded_url.rsplit('/', 1)[1] == quote_id:
                content.full_text = content.full_text.replace(url['url'], '')
                break
    try:
        m_count = len(content.extended_entities['media'])
        for m in content.entities['media']:
            content.full_text = content.full_text.replace(m['url'], '')
    except:
        pass
    message += (' {content.user.name}: {content.full_text}').format(content=content)
    try:
        if m_count > 1:
            message += ' ({0} images attached)'.format(m_count)
        else:
            message += ' (1 image attached)'
    except:
        pass
    message = message.strip()
#    all_urls = ((u['url'], u['expanded_url']) for u in all_urls)
#    all_urls = sorted(all_urls, key=lambda pair: len(pair[1]))
#    #code to not expand if it'd expand past 450
#    for url in all_urls:
#        replaced = message.replace(url[0], url[1])
#        if len(replaced) < 450:  # 400 is a guess to keep the privmsg < 510
#            message = replaced
#        else:
#            break

    timef = format_time(bot.db, bot.config, get_timezone(bot.db, bot.config, None, trigger.nick, trigger.sender), trigger.nick, trigger.sender, content.created_at)
    message += ' | Posted on {0}'.format(timef)

    bot.say(message)
