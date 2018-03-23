# 2016.12.24 03:29:54 CST
#Embedded file name: modules/courses.py
from sopel.module import commands, example
import requests
from lxml.html import fromstring

@commands('coursebook', 'cb', 'class', 'course')
@example('.cb cs2336')
def course_command(bot, trigger):
    """Search the UTD catalog for a course by prefix and number"""
    course = trigger.group(2).replace(' ', '').lower()
    url = 'https://catalog.utdallas.edu/now/undergraduate/courses/{}'.format(course)
    data = requests.get(url)
    tree = fromstring(data.content)
    tag = tree.find(".//div[@id='bukku-page']/p")
    text = tag.text_content()
    if not text:
        bot.say("Course not found.")
        return
    bot.say(text)
