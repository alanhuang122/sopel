#!/usr/local/bin/python
#coding: latin-1

from sopel.module import commands
import requests, operator
from bs4 import BeautifulSoup as Soup

@commands('results', 'resultsa')
def results_command(bot, trigger):
    """Latest results from The Guardian from the 2017 UK General Election"""
    seats = {}
    diff = {}
    URL = 'https://www.theguardian.com/politics/ng-interactive/2017/jun/08/live-uk-election-results-in-full-2017'
    soup = Soup(requests.get(URL).text, 'html.parser')
    tories = soup.find_all('li', 'ge-sop__party ge-sop__party--con')[0].find_all('p', 'ge-sop__party__seats')[0]
    seats['Conservatives'] = int(tories.text)
    torydiff = tories.next_sibling.next_sibling.text.strip()
    if torydiff != '(0)':
        diff['Conservatives'] = int(torydiff[1:-1])
    labour = soup.find_all('li', 'ge-sop__party ge-sop__party--lab')[0].find_all('p', 'ge-sop__party__seats')[0]
    seats['Labour'] = int(labour.text)
    labourdiff = labour.next_sibling.next_sibling.text.strip()
    if labourdiff != '(0)':
        diff['Labour'] = int(labourdiff[1:-1])
    libdem = soup.find_all('li', 'ge-sop__party ge-sop__party--libdem')[0].find_all('p', 'ge-sop__party__seats')[0]
    seats['Liberal Democrats'] = int(libdem.text)
    libdemdiff = libdem.next_sibling.next_sibling.text.strip()
    if libdemdiff != '(0)':
        diff['Liberal Democrats'] = int(libdemdiff[1:-1])
    snp = soup.find_all('li', 'ge-sop__party ge-sop__party--snp')[0].find_all('p', 'ge-sop__party__seats')[0]
    seats['SNP'] = int(snp.text)
    snpdiff = snp.next_sibling.next_sibling.text.strip()
    if snpdiff != '(0)':
        diff['SNP'] = int(snpdiff[1:-1])

    dup = soup.find_all('li', 'ge-sop__party ge-sop__party--dup')[0].contents[3].text.split(None)
    seats['Democratic Unionist Party'] = int(dup[0])
    diff['Democratic Unionist Party'] = int(dup[1][1:-1])
    ukip = soup.find_all('li', 'ge-sop__party ge-sop__party--ukip')[0].contents[3].text.split(None)
    seats['UKIP'] = int(ukip[0])
    diff['UKIP'] = int(ukip[1][1:-1])
    green = soup.find_all('li', 'ge-sop__party ge-sop__party--green')[0].contents[3].text.split(None)
    seats['Green'] = int(green[0])
    diff['Green'] = ' '.join(green[1][1:-1])
    oth = soup.find_all('li', 'ge-sop__party')[-1].contents[3].text.split(None)[0]
    seats['Others'] = int(oth)

    sort = sorted(seats.items(), key=operator.itemgetter(1), reverse=True)
    message = ''
    for e in sort:
        if e[0] is not 'Others' and e[1] is not 0:
            if e[0] in diff:
                if diff[e[0]] > 0:
                    message += '{0}: {1} (+{2}); '.format(e[0], e[1], diff[e[0]])
                elif diff[e[0]] < 0:
                    message += '{0}: {1} ({2}); '.format(e[0], e[1], diff[e[0]])
            else:
                message += '{0}: {1}; '.format(e[0], e[1])
    message += '{0}: {1}'.format('Others', seats['Others'])
    bot.say(message)

parties = { 'C'   : 'Conservatives',
            'SDLP': 'Social Democratic and Labour Party',
            'LD'  : 'Liberal Democrats',
            'Lab' : 'Labour',
            'UUP' : 'Ulster Unionist Party',
            'PC'  : 'Plaid Cymru',
            'DUP' : 'Democratic Unionist Party',
            'SF'  : 'Sinn Féin'}

@commands('resultsb')
def alternate_results(bot, trigger):
    seats = {}
    diffs = {}
    URL = 'https://int.nyt.com/newsgraphics/2017/06/uk-election/results-live.json'
    data = requests.get(URL).json()
    message = ''
    plist = data['summary']['results'].keys()
    plist.remove('Others')
    for party in plist:
        po = data['summary']['results'][party]
        if po['seats'] is not None:
            seats[party] = po['seats']
            if po['gains'] is None:
                po['gains'] = 0
            if po['losses'] is None:
                po['losses'] = 0
            diffs[party] = po['gains'] - po['losses']
    sorted_x = sorted(seats.items(), key=operator.itemgetter(1), reverse=True)
    for e in sorted_x:
        if e[0] in parties:
            if diffs[e[0]] > 0:
                message += '{0}: {1} (+{2}); '.format(parties[e[0]], e[1], diffs[e[0]])
            elif diffs [e[0]] < 0:
                message += '{0}: {1} ({2}); '.format(parties[e[0]], e[1], diffs[e[0]])
            else:
                message += '{0}: {1}; '.format(parties[e[0]], e[1])
        else:
            if diffs[e[0]] > 0:
                message += '{0}: {1} (+{2}); '.format(e[0], e[1], diffs[e[0]])
            elif diffs [e[0]] < 0:
                message += '{0}: {1} ({2}); '.format(e[0], e[1], diffs[e[0]])
            else:
                message += '{0}: {1}; '.format(e[0], e[1])
    party = 'Others'
    po = data['summary']['results'][party]
    if po['seats'] is not None:
        seats[party] = po['seats']
        if po['gains'] is not None and po['losses'] is not None:
            diffs[party] = po['gains'] - po['losses']
    if 'Others' in diffs:
        if diffs['Others'] > 0:
            message += '{0}: {1} (+{2}); '.format('Others', e[1], diffs[e[0]])
        elif diffs [e[0]] < 0:
            message += '{0}: {1} ({2}); '.format('Others', e[1], diffs[e[0]])
    else:
        message += '{0}: {1}; '.format('Others', seats['Others'])
    message = message[:-2]
    bot.say(message)
