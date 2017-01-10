from Crypto.Cipher import AES
from base64 import b64decode
import urllib2
import json
import sopel.module

def first(text,key,iv):
    ecb = AES.new(key, AES.MODE_ECB, iv)
    return ecb.decrypt(b64decode(text))[:16]
    
def second(text,key,iv):
    ecb = AES.new(key, AES.MODE_CBC, iv)
    return ecb.decrypt(b64decode(text))[16:].replace('\x0c','')
    
def decrypt(text,key,iv):
    return first(text,key,iv)+second(text,key,iv)

def getEntry(database,key,iv):
    response = urllib2.urlopen(database+"livingstories:142")
    entry = json.loads(response.read())
    return decrypt(entry.get('body'),key,iv)
    
def getQualitiesAffected(database,key,iv):
    entry = json.loads(getEntry(database,key,iv))
    return entry.get('QualitiesAffected')
    
def getMelt(database,key,iv):
    qualities = getQualitiesAffected(database,key,iv)
    for qual in qualities:
        if qual.get("AssociatedQuality").get("Id") == 106573:
            return qual.get("ChangeByAdvanced")
    
@sopel.module.commands('melt')
def melt(bot,trigger):
    rate=getMelt(bot.config.melt.database,bot.config.melt.key,b64decode(bot.config.melt.iv))
    if rate == None:
        bot.say("No melt rate")
        return
    bot.say("Current Melt Rate :"+rate)