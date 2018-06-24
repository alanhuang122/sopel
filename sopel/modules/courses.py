# 2016.12.24 03:29:54 CST
#Embedded file name: modules/courses.py
from lxml.html import fromstring
import re
import requests
from sopel.module import commands, example

@commands('coursebook', 'cb', 'class', 'course')
@example('.cb cs2336')
def course_command(bot, trigger):
    """Search the UTD catalog for a course by prefix and number"""
    course = trigger.group(2).replace(' ', '').lower()
    url = 'https://catalog.utdallas.edu/now/undergraduate/courses/{}'.format(course)
    data = requests.get(url)
    tree = fromstring(data.content)
    title = tree.find(".//div[@id='bukku-page']/h1").text_content()
    if not title:
        bot.say("Course not found.")
        return
    desc = tree.find(".//div[@id='bukku-page']/p").text_content()
    print(desc)
    hourstring = re.search(r'(\(.+?\))', desc).group(1)
    try:
        print(desc.rsplit('Prerequisite', 1)[1].rsplit(None, 2))
        prereqs, hours, freq = desc.rsplit('Prerequisite', 1)[1].rsplit(None, 2)
        prereqs = prereqs.replace('.', '')
        print(prereqs)
    except IndexError:
        prereqs = None
        _, hours, freq = desc.rsplit(None, 2)
    lecture, lab = hours[1:-1].rsplit('-', 1)
    if freq == 'S':
        frequency = 'Offered at least once per long semester'
    elif freq == 'Y':
        frequency = 'Offered at least once per year'
    elif freq == 'T':
        frequency = 'Offered at least once every two years'
    elif freq == 'R':
        frequency = 'Offered based on demand'
    else:
        frequency = 'Unknown frequency {}'.format(freq)
    if prereqs:
        string = '{} {} ({} hours lecture, {} hours lab) Prerequisite{}; Frequency: {}'.format(title, hourstring, lecture, lab, prereqs, frequency)
    else:
        string = '{} {} ({} hours lecture, {} hours lab); Frequency: {}'.format(title, hourstring, lecture, lab, frequency)
    bot.say(string)

@commands('desc')
def desc_command(bot, trigger):
    course = trigger.group(2).replace(' ', '').lower()
    url = 'https://catalog.utdallas.edu/now/undergraduate/courses/{}'.format(course)
    data = requests.get(url)
    tree = fromstring(data.content)
    desc = tree.find(".//div[@id='bukku-page']/p").text_content()
    if not desc:
        bot.say('Course not found.')
        return
    desc = desc.rsplit('Prerequisites', 1)[0]
    bot.say(desc)
