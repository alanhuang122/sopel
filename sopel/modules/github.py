# coding=utf8


from sopel.module import commands, rule, NOLIMIT
from sopel.tools.time import get_timezone, format_time

import operator, requests
import json
import re
import datetime
from requests import HTTPError

issueURL = (r'https?://(?:www\.)?github.com/([A-z0-9\-_]+/[A-z0-9\-_]+)/(?:issues|pull)/([\d]+)(?:#issuecomment-([\d]+))?')
commitURL = (r'https?://(?:www\.)?github.com/([A-z0-9\-_]+/[A-z0-9\-_]+)/(?:commit)/([A-z0-9\-]+)')
regex = re.compile(issueURL)
commitRegex = re.compile(commitURL)
repoRegex = re.compile('github\.com/([^ /]+?)/([^ /]+)/?(?!\S)')
sopel_instance = None

def fetch_api_endpoint(bot, url):
    oauth = ''
#    if bot.config.github.client_id and bot.config.github.secret:
#        oauth = '?client_id=%s&client_secret=%s' % (bot.config.github.client_id, bot.config.github.secret)
    return requests.get(url + oauth).text

@rule('.*%s.*' % issueURL)
def issue_info(bot, trigger, match=None):
    match = match or trigger
    URL = 'https://api.github.com/repos/%s/issues/%s' % (match.group(1), match.group(2))
    if match.group(3):
        URL = 'https://api.github.com/repos/%s/issues/comments/%s' % (match.group(1), match.group(3))

    try:
        raw = fetch_api_endpoint(bot, URL)
    except HTTPError:
        bot.say('[Github] API returned an error.')
        return NOLIMIT
    data = json.loads(raw)
    try:
        if len(data['body'].split('\n')) > 1 and len(data['body'].split('\n')[0]) > 180:
            body = data['body'].split('\n')[0] + '...'
        elif len(data['body'].split('\n')) > 2 and len(data['body'].split('\n')[0]) < 180:
            body = ' '.join(data['body'].split('\n')[:2]) + '...'
        else:
            body = data['body'].split('\n')[0]
    except KeyError:
        bot.say('[Github] API says this is an invalid issue. Please report this if you know it\'s a correct link!')
        return NOLIMIT

    if body.strip() == '':
        body = 'No description provided.'

    response = [
        '[Github]',
        ' [',
        match.group(1),
        ' #',
        match.group(2),
        '] ',
        data['user']['login'],
        ': '
    ]

    if 'title' in data:
        response.append(data['title'])
        response.append(' | ')
    response.append(body)

    bot.say(''.join(response))


@rule('.*%s.*' % commitURL)
def commit_info(bot, trigger, match=None):
    match = match or trigger
    URL = 'https://api.github.com/repos/%s/commits/%s' % (match.group(1), match.group(2))

    try:
        raw = fetch_api_endpoint(bot, URL)
    except HTTPError:
        bot.say('[Github] API returned an error.')
        return NOLIMIT
    data = json.loads(raw)
    try:
        if len(data['commit']['message'].split('\n')) > 1:
            body = data['commit']['message'].split('\n')[0] + '...'
        else:
            body = data['commit']['message'].split('\n')[0]
    except KeyError:
        bot.say('[Github] API says this is an invalid commit. Please report this if you know it\'s a correct link!')
        return NOLIMIT

    if body.strip() == '':
        body = 'No commit message provided.'

    response = [
        '[Github]',
        ' [',
        match.group(1),
        '] ',
        data['author']['login'],
        ': ',
        body,
        ' | ',
        str(data['stats']['total']),
        ' changes in ',
        str(len(data['files'])),
        ' files'
    ]
    bot.say(''.join(response))


def get_data(bot, trigger, URL):
    URL = URL.split('#')[0]
    try:
        raw = fetch_api_endpoint(bot, URL)
        rawLang = fetch_api_endpoint(bot, URL + '/languages')
    except HTTPError:
        bot.say('[Github] API returned an error.')
        return NOLIMIT
    data = json.loads(raw)
    langData = list(json.loads(rawLang).items())
    langData = sorted(langData, key=operator.itemgetter(1), reverse=True)

    if 'message' in data:
        return bot.say('[Github] %s' % data['message'])

    max = sum([pair[1] for pair in langData])

    data['language'] = ''
    for (key, val) in langData[:3]:
        data['language'] += str("{0:.1f}".format(float(val) / max * 100)) + '% ' + key + ' '

    if len(langData) > 3:
        remainder = sum([pair[1] for pair in langData[3:]])
        data['language'] += str("{0:.1f}".format(float(remainder) / max * 100)) + '% Other' + ' '

    timezone = get_timezone(bot.db, bot.config, None, trigger.nick)
    if not timezone:
        timezone = 'UTC'
    data['pushed_at'] = format_time(bot.db, bot.config, timezone, trigger.nick, trigger.sender, from_utc(data['pushed_at']))

    return data


@rule(r'.*https?://github\.com/([^ /]+?)/([^ /]+)/?(?!\S).*')
def data_url(bot, trigger):
    URL = 'https://api.github.com/repos/%s/%s' % (trigger.group(1).strip(), trigger.group(2).strip())
    fmt_response(bot, trigger, URL, True)


@commands('github', 'gh')
def github_repo(bot, trigger, match=None):
    match = match or trigger
    repo = match.group(2) or match.group(1)

    if repo.lower() == 'status':
        current = requests.get('https://status.github.com/api/status.json').json()
        lastcomm = requests.get('https://status.github.com/api/last-message.json').json()

        status = current['status']
        if status == 'major':
            status = "\x02\x034Broken\x03\x02"
        elif status == 'minor':
            status = "\x02\x037Shakey\x03\x02"
        elif status == 'good':
            status = "\x02\x033Online\x03\x02"

        lstatus = lastcomm['status']
        if lstatus == 'major':
            lstatus = "\x02\x034Broken\x03\x02"
        elif lstatus == 'minor':
            lstatus = "\x02\x037Shakey\x03\x02"
        elif lstatus == 'good':
            lstatus = "\x02\x033Online\x03\x02"

        timezone = get_timezone(bot.db, bot.config, None, trigger.nick)
        if not timezone:
            timezone = 'UTC'
        lastcomm['created_on'] = format_time(bot.db, bot.config, timezone, trigger.nick, trigger.sender, from_utc(lastcomm['created_on']))

        return bot.say('[Github] Current Status: ' + status + ' | Last Message: ' + lstatus + ': ' + lastcomm['body'] + ' (' + lastcomm['created_on'] + ')')
    elif repo.lower() == 'rate-limit':
        return bot.say(fetch_api_endpoint(bot, 'https://api.github.com/rate_limit'))

    if '/' not in repo:
        repo = trigger.nick.strip() + '/' + repo
    URL = 'https://api.github.com/repos/%s' % (repo.strip())

    fmt_response(bot, trigger, URL)


def from_utc(utcTime, fmt="%Y-%m-%dT%H:%M:%SZ"):
    """
    Convert UTC time string to time.struct_time
    """
    return datetime.datetime.strptime(utcTime, fmt)


def fmt_response(bot, trigger, URL, from_regex=False):
    data = get_data(bot, trigger, URL)

    if not data:
        return

    response = [
        '[Github]',
        ' ',
        str(data['full_name'])
    ]

    if data['description'] != None:
        response.append(' - ' + str(data['description']))

    if not data['language'].strip() == '':
        response.extend([' | ', data['language'].strip()])

    response.extend([
        ' | Last Push: ',
        str(data['pushed_at']),
        ' | Open Issues: ',
        str(data['open_issues'])
    ])

    if not from_regex:
        response.extend([' | ', data['html_url']])

    bot.say(''.join(response))
