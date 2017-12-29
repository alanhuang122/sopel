from Crypto.Cipher import AES
from base64 import b64decode
import requests
import json
from sopel.module import commands

def first(text,key):
    ecb = AES.new(key, AES.MODE_ECB)
    return ecb.decrypt(b64decode(text))[:16]

def second(text,key,iv):
    ecb = AES.new(key, AES.MODE_CBC, iv)
    return ecb.decrypt(b64decode(text))[16:].replace('\x0c','')

def decrypt(text):
    key = 'eyJUaXRsZSI6Ildo'
    iv = b64decode('7ENDyFzB5uxEtjFCpRpj3Q==')
    return first(text,key)+second(text,key,iv)

def get(id):
    data = requests.get('http://couchbase-fallenlondon.storynexus.com:4984/sync_gateway_json/{}'.format(id), headers={'Host': 'couchbase-fallenlondon.storynexus.com:4984', 'User-Agent': None, 'Accept-Encoding': None, 'Connection': None}).json()
    return decrypt(data['body'])

def clean(s):
    temp = s.rsplit('}', 1)
    return '{}}}'.format(temp[0])

def acquire(id):
    return json.loads(unicode(clean(get(id)), 'utf-8'))

def get_rate():
    j = acquire('livingstories:142')
    for q in j['QualitiesAffected']:
        if q.get("AssociatedQuality").get("Id") == 106573:
            return q.get("ChangeByAdvanced")
    
@commands('melt')
def melt(bot,trigger):
    rate = get_rate()
    if not rate:
        bot.say("No melt rate")
        return
    bot.say("Current Melt Rate: "+rate)
