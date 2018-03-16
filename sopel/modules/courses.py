# 2016.12.24 03:29:54 CST
#Embedded file name: modules/courses.py
from sopel.module import commands, example
import urllib.request, urllib.error, urllib.parse
import re

def chunkstring(string, length):
    return (string[0 + i:length + i] for i in range(0, len(string), length))


@commands('coursebook', 'cb', 'class', 'course')
@example('.cb cs2336')
def course_command(bot, trigger):
    """Search the UTD catalog for a course by prefix and number"""
    course = trigger.group(2)
    course = course.replace(' ', '')
    course = course.lower()
    url = 'https://catalog.utdallas.edu/2016/undergraduate/courses/{}'.format(course)
    data = urllib.request.urlopen(url)
    string = None
    for line in data:
        if re.search('(<span.+)', line) is not None:
            string = re.search('(<span.+)', line).group(0)
            break

    if not string:
        bot.say("I didn't understand your input.")
        return
    string = re.sub('(</?a.*?>)', '', string)
    string = re.search('(?:<h1>)(.+)(?:</h1>.+</span> )(.+?)(?:</p>)', string)
    if not string:
        bot.say("I didn't understand your input.")
        return
    string = '{0}: {1}'.format(string.group(1), string.group(2))
    for line in chunkstring(string, 435):
        bot.say(line)
