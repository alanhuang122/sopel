#!/usr/bin/env python
# vim: set fileencoding=UTF-8 :
"""
weather.py - bot Weather Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.
"""
from sopel.module import commands

import requests
import json
import re
import googlemaps
from datetime import datetime
from sopel.tools.icao import data
from sopel.tools.time import format_time, get_timezone
import urllib.request, urllib.parse, urllib.error

install_geopy = "Please install geopy via 'pip' to use weather.py"

try:
    import geopy
except ImportError:
    print(install_geopy)

def setup(bot):
    global gmaps
    gmaps = googlemaps.Client(key=bot.config.google.api_key, timeout=5)

r_from = re.compile(r'(?i)([+-]\d+):00 from')
r_tag = re.compile(r'<(?!!)[^>]+>')

def clean(txt, delim=''):
    '''Remove HTML entities from a given text'''
    if delim:
        return r_tag.sub(delim, txt)
    else:
        return r_tag.sub('', txt)

def f_loc(address_components):
    for c in address_components:
        if 'locality' in c['types']:
            city = c['long_name']
        elif 'administrative_area_level_1' in c['types']:
            state = c['long_name']
        elif 'administrative_area_level_2' in c['types']:
            county = c['long_name']
        elif 'country' in c['types']:
            country = c['long_name']
    parts = []
    try:
        parts.append(city)
    except:
        pass
    try:
        parts.append(county)
    except:
        pass
    try:
        parts.append(state)
    except:
        pass
    try:
        parts.append(country)
    except:
        pass
    return ', '.join(parts)

def location(name):
    location = gmaps.geocode(name)[0]

    try:
        outgoing_name = f_loc(location['address_components'])
        lat = location['geometry']['location']['lat']
        lng = location['geometry']['location']['lng']
    except AttributeError:
        return '', '', ''

    return outgoing_name, str(lat), str(lng)


class GrumbleError(object):
    pass


def local(icao, hour, minute):
    '''Grab local time based on ICAO code'''
    uri = ('http://www.flightstats.com/' +
             'go/Airport/airportDetails.do?airportCode=%s')
    try: bytes = requests.get(uri % icao).text
    except AttributeError:
        raise GrumbleError('A WEBSITE HAS GONE DOWN WTF STUPID WEB')
    m = r_from.search(bytes)
    if m:
        offset = m.group(1)
        lhour = int(hour) + int(offset)
        lhour = lhour % 24
        return (str(lhour) + ':' + str(minute) + ', ' + str(hour) +
                  str(minute) + 'Z')
    return str(hour) + ':' + str(minute) + 'Z'


def code(bot, search):
    '''Find ICAO code in the provided database.py (findest the nearest one)'''
    if search.upper() in data:
        return search.upper()
    else:
        name, latitude, longitude = location(search)
        if name == '?': return False
        sumOfSquares = (99999999999999999999999999999, 'ICAO')
        for icao_code in data:
            lat = float(data[icao_code][0])
            lon = float(data[icao_code][1])
            latDiff = abs(float(latitude) - float(lat))
            lonDiff = abs(float(longitude) - float(lon))
            diff = (latDiff * latDiff) + (lonDiff * lonDiff)
            if diff < sumOfSquares[0]:
                sumOfSquares = (diff, icao_code)
        return sumOfSquares[1]


def get_metar(icao_code):
    '''Obtain METAR data from NOAA for a given ICAO code'''

    uri = 'http://tgftp.nws.noaa.gov/data/observations/metar/stations/%s.TXT'

    try:
        page = requests.get(uri % icao_code)
    except AttributeError:
        raise GrumbleError('OH CRAP NOAA HAS GONE DOWN THE WEB IS BROKEN')
    if 'Not Found' in page:
        return False, icao_code + ': no such ICAO code, or no NOAA data.'

    return True, page


def get_icao(bot, inc, command='weather'):
    '''Provide the ICAO code for a given input'''

    if not inc:
        return False, 'Try .%s London, for example?' % (command)

    icao_code = code(bot, inc)

    if not icao_code:
        return False, 'No ICAO code found, sorry.'

    return True, icao_code


@commands('metar')
def show_metar(bot, input):
    '''.metar <location> -- shows the raw METAR data for a given location'''
    txt = input.group(2)

    if not txt:
        return bot.say('Try .metar London, for example?')

    status, icao_code = get_icao(bot, txt, 'metar')
    if not status:
        return bot.say(icao_code)

    status, metar = get_metar(icao_code)
    if not status:
        return bot.say(metar)

    return bot.say(metar)


def speed_desc(speed):
    '''Provide a more natural description of wind speed'''
    description = str()

    if speed < 1:
        description = 'Calm'
    elif speed < 4:
        description = 'Light air'
    elif speed < 7:
        description = 'Light breeze'
    elif speed < 11:
        description = 'Gentle breeze'
    elif speed < 16:
        description = 'Moderate breeze'
    elif speed < 22:
        description = 'Fresh breeze'
    elif speed < 28:
        description = 'Strong breeze'
    elif speed < 34:
        description = 'Near gale'
    elif speed < 41:
        description = 'Gale'
    elif speed < 48:
        description = 'Strong gale'
    elif speed < 56:
        description = 'Storm'
    elif speed < 64:
        description = 'Violent storm'
    else: description = 'Hurricane'

    return description


def wind_dir(degrees):
    '''Provide a nice little unicode character of the wind direction'''
    if degrees == 'VRB':
        degrees = '\u21BB'
    elif (degrees <= 22.5) or (degrees > 337.5):
        degrees = '\u2191'
    elif (degrees > 22.5) and (degrees <= 67.5):
        degrees = '\u2197'
    elif (degrees > 67.5) and (degrees <= 112.5):
        degrees = '\u2192'
    elif (degrees > 112.5) and (degrees <= 157.5):
        degrees = '\u2198'
    elif (degrees > 157.5) and (degrees <= 202.5):
        degrees = '\u2193'
    elif (degrees > 202.5) and (degrees <= 247.5):
        degrees = '\u2199'
    elif (degrees > 247.5) and (degrees <= 292.5):
        degrees = '\u2190'
    elif (degrees > 292.5) and (degrees <= 337.5):
        degrees = '\u2196'

    return degrees


@commands('weather')
def f_weather(bot, input):
    '''.weather <ICAO> - Show the weather at airport with the code <ICAO>.'''

    text = input.group(2)

    status, icao_code = get_icao(bot, text)
    print('status:', status)
    print('icao_code:', icao_code)
    if not status:
        return bot.say(icao_code)

    status, page = get_metar(icao_code)
    page = page.text
    print('status:', status)
    print('page:', page)
    if not status:
        return bot.say(page)

    metar = page.splitlines().pop()
    metar = metar.split(' ')

    if len(metar[0]) == 4:
        metar = metar[1:]

    if metar[0].endswith('Z'):
        time = metar[0]
        metar = metar[1:]
    else: time = None

    if metar[0] == 'AUTO':
        metar = metar[1:]
    if metar[0] == 'VCU':
        bot.say(icao_code + ': no data provided')
        return

    if metar[0].endswith('KT'):
        wind = metar[0]
        metar = metar[1:]
    else: wind = None

    if ('V' in metar[0]) and (metar[0] != 'CAVOK'):
        vari = metar[0]
        metar = metar[1:]
    else: vari = None

    if ((len(metar[0]) == 4) or
         metar[0].endswith('SM')):
        visibility = metar[0]
        metar = metar[1:]
    else: visibility = None

    while metar[0].startswith('R') and (metar[0].endswith('L')
                                                or 'L/' in metar[0]):
        metar = metar[1:]

    if len(metar[0]) == 6 and (metar[0].endswith('N') or
                                        metar[0].endswith('E') or
                                        metar[0].endswith('S') or
                                        metar[0].endswith('W')):
        metar = metar[1:] # 7000SE?

    cond = []
    while (((len(metar[0]) < 5) or
             metar[0].startswith('+') or
             metar[0].startswith('-')) and (not (metar[0].startswith('VV') or
             metar[0].startswith('SKC') or metar[0].startswith('CLR') or
             metar[0].startswith('FEW') or metar[0].startswith('SCT') or
             metar[0].startswith('BKN') or metar[0].startswith('OVC')))):
        cond.append(metar[0])
        metar = metar[1:]

    while '/P' in metar[0]:
        metar = metar[1:]

    if not metar:
        return bot.say(icao_code + ': no data provided')

    cover = []
    while (metar[0].startswith('VV') or metar[0].startswith('SKC') or
             metar[0].startswith('CLR') or metar[0].startswith('FEW') or
             metar[0].startswith('SCT') or metar[0].startswith('BKN') or
             metar[0].startswith('OVC')):
        cover.append(metar[0])
        metar = metar[1:]
        if not metar:
            return bot.say(icao_code + ': no data provided')

    if metar[0] == 'CAVOK':
        cover.append('CLR')
        metar = metar[1:]

    if metar[0] == 'PRFG':
        cover.append('CLR') # @@?
        metar = metar[1:]

    if metar[0] == 'NSC':
        cover.append('CLR')
        metar = metar[1:]

    if ('/' in metar[0]) or (len(metar[0]) == 5 and metar[0][2] == '.'):
        temp = metar[0]
        metar = metar[1:]
    else: temp = None

    if metar[0].startswith('QFE'):
        metar = metar[1:]

    if metar[0].startswith('Q') or metar[0].startswith('A'):
        pressure = metar[0]
        metar = metar[1:]
    else: pressure = None

    if time:
        day = time[0:2]
        hour = time[2:4]
        minute = time[4:6]
        utcnow = datetime.utcnow()
        print(utcnow)
        if utcnow.day == int(day):
            tz = get_timezone(bot.db, bot.config, None, input.nick, input.sender)
            obs_time = datetime(utcnow.year, utcnow.month, utcnow.day, int(hour), int(minute))
            time = format_time(bot.db, bot.config, tz, input.nick, input.sender, obs_time)
        else:
            time = local(icao_code, hour, minute)
    else: time = '(time unknown)'

    speed = False

    if wind:
        ## if the text that is in wind[3:5] can't be converted to float
        ## default to 0, this happens in rare cases when there is extra info
        ## in the METAR data that either removes or replaces wind speed
        try:
            speed = float(wind[3:5])
        except:
            speed = 0

        description = speed_desc(speed)

        try:
            degrees = float(wind[0:3])
        except:
            degrees = 0
        degrees = wind_dir(degrees)

        if not icao_code.startswith('EN') and not icao_code.startswith('ED'):
            ## for any part of the world except Germany and Norway
            wind = '%s %.1fkt (%s)' % (description, speed, degrees)
        elif icao_code.startswith('ED'):
            ## Germany
            kmh = float(speed * 1.852)
            wind = '%s %.1fkm/h (%.1fkt) (%s)' % (description, kmh, speed, degrees)
        elif icao_code.startswith('EN'):
            ## Norway
            ms = float(speed * 0.514444444)
            wind = '%s %.1fm/s (%.1fkt) (%s)' % (description, ms, speed, degrees)
    else: wind = '(wind unknown)'

    if visibility:
        visibility = visibility + 'm'
    else: visibility = '(visibility unknown)'

    if cover:
        level = None
        for c in cover:
            if c.startswith('OVC') or c.startswith('VV'):
                if (level is None) or (level < 8):
                    level = 8
            elif c.startswith('BKN'):
                if (level is None) or (level < 5):
                    level = 5
            elif c.startswith('SCT'):
                if (level is None) or (level < 3):
                    level = 3
            elif c.startswith('FEW'):
                if (level is None) or (level < 1):
                    level = 1
            elif c.startswith('SKC') or c.startswith('CLR'):
                if level is None:
                    level = 0

        if level == 8:
            cover = 'Overcast \u2601'
        elif level == 5:
            cover = 'Cloudy'
        elif level == 3:
            cover = 'Scattered'
        elif (level == 1) or (level == 0):
            cover = 'Clear \u263C'
        else: cover = 'Cover Unknown'
    else: cover = 'Cover Unknown'

    if temp:
        if '/' in temp:
            t = temp.split('/')
            temp = t[0]
            dew = t[1]
        else: temp = temp.split('.')[0]
        if temp.startswith('M'):
            temp = '-' + temp[1:]
        if dew.startswith('M'):
            dew = '-' + dew[1:]
        try:
            temp = float(temp)
            dew = float(dew)
        except ValueError:
            temp = '?'
            dew = '?'
    else:
        temp = '?'
        dew = '?'

    windchill = False
    if isinstance(temp, float) and isinstance(speed, float) and temp <= 10.0 and speed > 0:
        ## Convert knots to kilometers per hour, https://is.gd/3dNrbW
        speed_kmh = speed * 1.852

        ## Formula for Windchill: https://is.gd/SS0u6E
        windchill = 13.12 + (0.6215 * temp) - (11.37 * (speed_kmh ** (0.16))) + (0.3965 * temp * (speed_kmh ** (0.16)))
        windchill = float(windchill)

        ## convert result into Fahrenheit
        f = (windchill * 1.8) + 32

        if icao_code.startswith('K'):
            ## if in North America
            windchill = '%.1f\u00B0F (%.1f\u00B0C)' % (f, windchill)
        else:
            ## else, anywhere else in the worldd
            windchill = '%.1f\u00B0C' % (windchill)

    heatindex = False
    if isinstance(temp, float) and isinstance(dew, float):
        rh = make_rh_C(temp, dew)
        temp_f = (temp * 1.8) + 32.0
        if rh >= 40.0 and temp_f >= 80.0:
            heatindex = gen_heat_index(temp_f, rh)
            heatindex = '%.1f\u00B0F (%.1f\u00B0C)' % (heatindex, (heatindex - 32.0) / (1.8) )

    if pressure:
        if pressure.startswith('Q'):
            pressure = pressure.lstrip('Q')
            if pressure != 'NIL':
                pressure = str(float(pressure)) + 'mb'
            else: pressure = '?mb'
        elif pressure.startswith('A'):
            pressure = pressure.lstrip('A')
            if pressure != 'NIL':
                inches = pressure[:2] + '.' + pressure[2:]
                mb = float(inches) * 33.7685
                pressure = '%sin (%.2fmb)' % (inches, mb)
            else: pressure = '?mb'

            if isinstance(temp, float):
                f = (temp * 1.8) + 32
                temp = '%.1f\u00B0F (%.1f\u00B0C)' % (f, temp)
            if isinstance(dew, float):
                f = (dew * 1.8) + 32
                dew = '%.1f\u00B0F (%.1f\u00B0C)' % (f, dew)
    else: pressure = '?mb'

    if isinstance(temp, float):
        temp = '%.1f\u00B0C' % temp
    if isinstance(dew, float):
        dew = '%.1f\u00B0C' % dew

    if cond:
        conds = cond
        cond = ''

        intensities = {
            '-': 'Light',
            '+': 'Heavy'
        }

        descriptors = {
            'MI': 'Shallow',
            'PR': 'Partial',
            'BC': 'Patches',
            'DR': 'Drifting',
            'BL': 'Blowing',
            'SH': 'Showers of',
            'TS': 'Thundery',
            'FZ': 'Freezing',
            'VC': 'In the vicinity:',
            'RA': 'Unimaginable',
            'SN': 'Snow',
        }

        phenomena = {
            'DZ': 'Drizzle',
            'RA': 'Rain',
            'SN': 'Snow',
            'SG': 'Snow Grains',
            'IC': 'Ice Crystals',
            'PL': 'Ice Pellets',
            'GR': 'Hail',
            'GS': 'Small Hail',
            'UP': 'Unknown Precipitation',
            'BR': 'Mist',
            'FG': 'Fog',
            'FU': 'Smoke',
            'VA': 'Volcanic Ash',
            'DU': 'Dust',
            'SA': 'Sand',
            'HZ': 'Haze',
            'PY': 'Spray',
            'PO': 'Whirls',
            'SQ': 'Squalls',
            'FC': 'Tornado',
            'SS': 'Sandstorm',
            'DS': 'Duststorm',
            # ? Cf. http://swhack.com/logs/2007-10-05#T07-58-56
            'TS': 'Thunderstorm',
            'SH': 'Showers'
        }

        for c in conds:
            if c.endswith('//'):
                if cond: cond += ', '
                cond += 'Some Precipitation'
            elif len(c) == 5:
                intensity = intensities[c[0]]
                descriptor = descriptors[c[1:3]]
                phenomenon = phenomena.get(c[3:], c[3:])
                if cond: cond += ', '
                cond += intensity + ' ' + descriptor + ' ' + phenomenon
            elif len(c) == 4:
                descriptor = descriptors.get(c[:2], c[:2])
                phenomenon = phenomena.get(c[2:], c[2:])
                if cond: cond += ', '
                cond += descriptor + ' ' + phenomenon
            elif len(c) == 3:
                intensity = intensities.get(c[0], c[0])
                phenomenon = phenomena.get(c[1:], c[1:])
                if cond: cond += ', '
                cond += intensity + ' ' + phenomenon
            elif len(c) == 2:
                phenomenon = phenomena.get(c, c)
                if cond: cond += ', '
                cond += phenomenon

    output = str()
    output += 'Cover: ' + cover
    output += ', Temp: ' + temp
    output += ', Dew Point: ' + dew
    if windchill:
        output += ', Windchill: ' + windchill
    if heatindex:
        output += ', Heat Index: ' + heatindex
    output += ', Pressure: ' + pressure
    if cond:
        output += ' Condition: ' + cond
    output += ', Wind: ' + wind
    output += ' - %s, %s' % (str(icao_code), time)


    bot.say(output)

@commands('windchill')
def windchill(bot, input):
    '''.windchill <temp> <wind speed> -- shows Windchill in F'''
    ## this is pretty hacky
    text = input.split()

    if len(text) == 1:
        ## show them what we want
        return bot.say('.windchill <temp> <wind speed> -- shows Windchill in \u00B0F')

    if len(text) >= 3:
        try:
            ## please, please, please be numbers...
            temp = float(text[1])
            wind = float(text[2])
        except:
            ## well, shit, there weren't numbers
            return bot.say('Invalid arguments! Try, .windchill without any parameters.')
    else:
        ## why couldn't the input be valid? silly users
        return bot.say('Invalid arguments! Try, .windchill without any parameters.')

    if temp > 50:
        return bot.say('The windchill formula only works on temperatures below 50 \u00B0F')

    if wind < 0:
        ## yes, yes, I know about vectors, but this is a scalar equation
        return bot.say("You can't have negative wind speed!")
    elif wind >= 300:
        ## hehe
        bot.reply('Are you okay?')

    ## cf. https://is.gd/mgLuzU
    wc = 35.74 + (0.6215 * temp) - (35.75 * (wind ** (0.16))) + (0.4275 * temp * (wind ** (0.16)))

    bot.say('Windchill: %2.f \u00B0F' % (wc))


dotw = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

def remove_dots(txt):
    if '..' not in txt:
        return txt
    else:
        txt = re.sub(r'\.+', ' ', txt)
        return remove_dots(txt)


def remove_spaces(x):
    if '  ' in x:
        x = x.replace('  ', ' ')
        return remove_spaces(x)
    else:
        return x


def chomp_desc(txt):
    out = txt
    #print "original:", out
    p = re.compile(r'(?<=[\.\?!]\s)(\w+)')

    def upper_repl(match):
        return match.group(1).upper()

    def cap(match):
        return match.group().capitalize()

    out = re.sub('([Tt])hunder(storm|shower)', r'\1\2', out)
    out = re.sub('with', 'w/', out)
    out = re.sub('and', '&', out)
    out = re.sub('during', 'in', out)
    out = re.sub('becoming', '', out)
    out = re.sub('occasionally', 'occ', out)
    out = re.sub('occasional', 'occ', out)
    out = re.sub('especially', 'esp.', out)
    out = re.sub('possibly', 'poss', out)
    out = re.sub('possible', 'poss', out)
    out = re.sub('([Ss])cattered', r'\1cat', out)
    out = re.sub('([Mm])orning', 'AM', out)
    out = re.sub('evening', 'AM', out)
    out = re.sub('afternoon', 'PM', out)
    out = re.sub('in the', 'in', out)
    #out = re.sub(r'\.\.', ' ', out)
    out = re.sub('Then the (\S)', upper_repl, out)
    out = re.sub(r'(?i)(\b)(?:the|a)(\b)', r'\1\2', out)
    #out = re.sub(cap, '', out)

    out = remove_dots(out)
    out = remove_spaces(out)

    out = p.sub(cap, out)

    out = out.strip()
    return out

def make_rh_C(temp, dewpoint):
    return 100.0 - (5.0 * (temp - dewpoint))


def make_rh_F(temp, dewpoint):
    return 100.0 - ((25.0 / 9.0) * (temp - dewpoint))


def gen_heat_index(temp, rh):
    ## based on https://en.wikipedia.org/wiki/Heat_index#Formula
    c1 = -42.379
    c2 = 2.04901523
    c3 = 10.14333127
    c4 = -0.22475541
    c5 = -6.83783 * (10 ** (-3))
    c6 = -5.481717 * (10 ** (-2))
    c7 = 1.22874 * (10 ** (-3))
    c8 = 8.5282 * (10 ** (-4))
    c9 = -1.99 * (10 ** (-6))

    heat_index = c1 + c2*temp + c3*rh + c4*temp*rh + c5*temp*temp + c6*rh*rh + c7*temp*temp*rh + c8*temp*rh*rh + c9*temp*temp*rh*rh
    return heat_index

def add_degree(txt):
    if ' F' in txt:
        txt = re.sub(' F', '\u00B0F', txt)
    else:
        txt = re.sub('F', '\u00B0F', txt)

    if ' C' in txt:
        txt = re.sub(' C', '\u00B0C', txt)
    else:
        txt = re.sub('C', '\u00B0C', txt)
    return txt


@commands('wu')
def weather_wunderground(bot, input):
    if not hasattr(bot.config, 'wunderground_apikey'):
        return bot.say('Please sign up for a wunderground.com API key at https://www.wunderground.com/weather/api/ or try .wx-noaa or .weather-noaa')

    apikey = bot.config.wunderground_apikey

    url = 'https://api.wunderground.com/api/%s/conditions/geolookup/q/%s.json'
    txt = input.group(2)
    if not txt:
        return bot.say('No input provided. Please provide a locaiton.')

    txt = txt

    url_new = url % (apikey, urllib.parse.quote(txt))

    try:
        page = requests.get(url_new)
    except:
        return bot.say("We could not access wunderground.com's API at the moment.")

    useful = False

    try:
        useful = json.loads(page)
    except:
        return bot.say('We could not obtain useful information from the wunderground.com API.')

    if 'response' in useful and 'error' in useful['response'] and 'description' in useful['response']['error']:
        return bot.say(str(useful['response']['error']['description']))

    if 'current_observation' not in useful:
        return bot.say('No observations currently found.')
    current = useful['current_observation']


    condition = current['weather']
    temp = current['temperature_string']
    wind_kph = current['wind_kph']
    wind_mph = current['wind_mph']
    wind_dir = current['wind_dir']
    feelslike = current['feelslike_string']
    dewpoint = current['dewpoint_string']
    location = current['observation_location']['full']
    time_updated = current['observation_time']
    precip_today = current['precip_today_string']
    #precip_1hr = current['precip_1hr_string']
    rh = current['relative_humidity']
    pressure_in = current['pressure_in']
    pressure_mb = current['pressure_mb']
    pressure_trend = current['pressure_trend']

    if pressure_trend == '-':
        #pressure_trend = re.sub('-', u'\u2193', pressure_trend)
        pressure_trend = '\u2193'
    elif pressure_trend == '+':
        #pressure_trend = re.sub('\+', u'\u2191', pressure_trend)
        pressure_trend = '\u2191'
    elif pressure_trend == '0':
        pressure_trend = '\u2192'

    time_updated = re.sub('Last Updated on ', '\x1FLast Updated\x1F: ', time_updated)

    output = str()
    output += '\x1FCover\x1F: ' + condition
    output += ', \x1FTemp\x1F: ' + add_degree(temp)
    output += ', \x1FDew Point\x1F: ' + add_degree(dewpoint)
    output += ', \x1FHumdity\x1F: ' + rh
    output += ', \x1FFeels Like\x1F: ' + add_degree(feelslike)
    output += ', \x1FPressure\x1F: ' + '[%s] %sin (%smb)' % (pressure_trend, pressure_in, pressure_mb)
    output += ', \x1FWind\x1F: ' + 'From the %s at %s mph (%s kmh)' % (wind_dir, wind_mph, wind_kph)
    output += ', \x1FLocation\x1F: ' + (location)
    output += ', ' + time_updated

    output += ', (Powered by wunderground.com)'

    bot.say(output)



def preface_location(ci, reg='', cty=''):
    out = str()
    out += '[' + ci
    if reg:
        out += ', ' + reg
    if cty:
        out += ', %s' % (cty)
    out += '] '
    return out

@commands('forecast-wg')
def forecast_wg(bot, input):
    if not hasattr(bot.config, 'wunderground_apikey'):
        return bot.say('Please sign up for a wunderground.com API key at https://www.wunderground.com/weather/api/ or try .wx-noaa or .weather-noaa')

    apikey = bot.config.wunderground_apikey

    url = 'https://api.wunderground.com/api/%s/forecast10day/geolookup/q/%s.json'

    txt = input.group(2)
    if not txt:
        return bot.say('No input provided. Please provide a locaiton.')

    url_new = url % (apikey, txt)

    try:
        page = requests.get(url_new)
    except:
        return bot.say("We could not access wunderground.com's API at the moment.")

    try:
        useful = json.loads(page)
    except:
        return bot.say('We could not obtain useful information from the wunderground.com API.')

    if 'response' in useful and 'error' in useful['response'] and 'description' in useful['response']['error']:
        return bot.say(str(useful['response']['error']['description']))

    if 'forecast' not in useful:
        return bot.say('We could not find a forecast for the given location.')

    days = useful['forecast']['simpleforecast']['forecastday']
    forecast_text = useful['forecast']['txt_forecast']['forecastday']

    days_text = list()

    for each in forecast_text:
        txt = each['fcttext']
        temp = txt.split('. Low')
        temp = temp[0]

        temp = temp.split('. High')
        temp = temp[0]

        temp = chomp_desc(temp)

        days_text.append(temp)

    city = useful['location']['city']

    region = str()
    if 'state' in useful['location']:
        region += useful['location']['state']

    country = useful['location']['country_name']

    output = preface_location(city, region, country)
    output_second = preface_location(city, region, country)

    k = 0
    for day in days:
        day_of_week = day['date']['weekday_short']
        conditions = day['conditions']
        highs = '\x02\x0304%s\u00B0F (%s\u00B0C)\x03\x02' % (day['high']['fahrenheit'], day['high']['celsius'])
        lows = '\x02\x0302%s\u00B0F (%s\u00B0C)\x03\x02' % (day['low']['fahrenheit'], day['low']['celsius'])
        #wind = 'From %s at %s-mph (%s-kph)' % (day['avewind']['dir'], day['maxwind']['mph'], day['maxwind']['kph'])

        days_text_temp = days_text[k]
        if not days_text[k].endswith('.'):
            days_text_temp += '.'

        days_text1_temp = days_text[k + 1]
        if not days_text[k + 1].endswith('.'):
            days_text1_temp += '.'

        temp = '\x02\x0310%s\x03\x02: %s / %s, AM: %s PM: %s | ' % (day_of_week, highs, lows, days_text_temp, days_text1_temp)

        k += 2
        if (k / 2.) <= 2:
            output += temp
        elif 4 >= (k / 2.) > 2:
            output_second += temp

    output = output[:-3]
    output_second = output_second[:-3]

    bot.say(output)
    bot.say(output_second)

@commands('radar-us')
def radar_us(bot, input):
    return bot.say('https://radar.weather.gov/Conus/Loop/NatLoop.gif')
