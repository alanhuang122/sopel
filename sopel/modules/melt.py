from Crypto.Cipher import AES
from base64 import b64decode
import requests
import json
import re
from sopel.module import commands, interval

cur_rate = None

def setup(bot):
    global cur_rate
    meltfile = open('/home/alan/fl-utils/data/rates.txt')
    lines = meltfile.readlines()
    meltfile.close()
    cur_rate = lines[-1].strip().split(None, 1)
    print(('[melt] cur_rate init to {}'.format(cur_rate)))

def first(text,key):
    ecb = AES.new(key, AES.MODE_ECB)
    return ecb.decrypt(b64decode(text))[:16]

def second(text,key,iv):
    ecb = AES.new(key, AES.MODE_CBC, iv)
    return ecb.decrypt(b64decode(text))[16:]

def decrypt(text):
    key = 'eyJUaXRsZSI6Ildo'
    iv = b64decode('7ENDyFzB5uxEtjFCpRpj3Q==')
    return (first(text,key)+second(text,key,iv)).decode('utf-8')

def get(id):
    data = requests.get('http://couchbase-fallenlondon.storynexus.com:4984/sync_gateway_json/{}'.format(id), headers={'Host': 'couchbase-fallenlondon.storynexus.com:4984', 'User-Agent': None, 'Accept-Encoding': None, 'Connection': None}).json()
    return decrypt(data['body'])

def clean(s):
    temp = s.rsplit('}', 1)
    return '{}}}'.format(temp[0])

def acquire(id):
    return json.loads(clean(get(id)))

def get_rate():
    j = acquire('livingstories:142')
    for q in j['QualitiesAffected']:
        if q.get("AssociatedQuality").get("Id") == 106573:
            return q.get("ChangeByAdvanced")

def get_costs():
    costs = []
    s = acquire('events:11404')
    for b in s['ChildBranches']:
        if 'Noman' in b.get('Name'):
            requirements = b['QualitiesRequired']
            for r in requirements:
                costs.append(Requirement(r))
            return '[{}]'.format(', '.join([str(r) for r in costs]))

class Quality:
    def __init__(self, jdata):
        self.name = jdata.get('Name', '(no name)')
        self.test_type = 'Narrow' if 'DifficultyTestType' in jdata else 'Broad'

    @classmethod
    def get(self, id):
        key = 'qualities:{}'.format(id)
        data = acquire(key)
        return Quality(data)

class Requirement:
    def __init__(self, jdata):
        self.raw = jdata
        self.quality = Quality.get(jdata['AssociatedQuality']['Id'])
        try:
            self.upper_bound = jdata['MaxLevel']
        except:
            try:
                self.upper_bound = sub_qualities(jdata['MaxAdvanced'])
            except KeyError:
                pass
        try:
            self.lower_bound = jdata['MinLevel']
        except:
            try:
                self.lower_bound = sub_qualities(jdata['MinAdvanced'])
            except KeyError:
                pass
        try:
            self.difficulty = jdata['DifficultyLevel']
        except:
            try:
                self.difficulty = sub_qualities(jdata['DifficultyAdvanced'])
            except KeyError:
                pass
        if hasattr(self, 'difficulty'):
            self.type = 'Challenge'
            self.test_type = self.quality.test_type
        else:
            self.type = 'Requirement'
        assert jdata.get('BranchVisibleWhenRequirementFailed') == jdata.get('VisibleWhenRequirementFailed')
        self.visibility = jdata.get('BranchVisibleWhenRequirementFailed', False)

    def __repr__(self):
        string = ''
        if not self.visibility:
            string += '[Branch hidden if failed] '
        if self.type == 'Challenge':
            if self.quality.id == 432:
                string += 'Luck: {}% chance'.format(50 - self.difficulty * 10)
            else:
                string += '{} {}: {} {}'.format(self.test_type, self.type, self.quality.name, self.difficulty)
        else:
            try:
                if self.lower_bound == self.upper_bound:
                    string += '{} exactly {}'.format(self.quality.name, self.lower_bound)
                else:
                    string += '{} [{}-{}]'.format(self.quality.name, self.lower_bound, self.upper_bound)
            except:
                try:
                    string += '{} at least {}'.format(self.quality.name, self.lower_bound)
                except:
                    string += '{} no more than {}'.format(self.quality.name, self.upper_bound)
        return string

def sub_qualities(string):
    for x in re.findall(r'\[qb?:(\d+)\]', string):
        string = string.replace(x, Quality.get(int(x)).name)
    return string

@commands('melt')
def melt(bot,trigger):
    rate = get_rate()
    if not rate:
        bot.say("No melt rate")
        return
    bot.say("Current Melt Rate: "+rate)

@commands('noman')
def noman_command(bot, trigger):
    costs = get_costs()
    if not costs:
        bot.say('No requirements...? Alan, help ;-;')
        return
    bot.say('Current requirements: {}'.format(costs))

@interval(30)
def melt_poll(bot):
    global cur_rate
    meltfile = open('/home/alan/fl-utils/data/rates.txt')
    lines = meltfile.readlines()
    meltfile.close()
    new_rate = lines[-1].strip().split(None, 1)
    if new_rate[1] != cur_rate[1]:
        cur_rate = new_rate
        bot.say('Melt rate has changed from {} to {}'.format(cur_rate, new_rate), '#alantest')
        bot.say('Melt rate has changed from {} to {}'.format(cur_rate, new_rate), '#fallenlondon')
