# coding=utf-8
"""
calc.py - Sopel Calculator Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

https://sopel.chat
"""

from collections import deque
import math
import requests
from requests.utils import quote
from sopel.module import commands, example
from sopel.tools.calculation import eval_equation
from requests import get
import sys

if sys.version_info.major < 3:
    from urllib import quote as _quote
    quote = lambda s: _quote(s.encode('utf-8')).decode('utf-8')
else:
    from urllib.parse import quote

if sys.version_info.major >= 3:
    chr = chr


BASE_TUMBOLIA_URI = 'https://tumbolia-sopel.appspot.com/'


@commands('rpn')
@example('.rpn 5 6 7 + *')
def rpn(bot, trigger):
    """
    Performs calculations entered using reverse polish notation.
    """
    if not trigger.group(2):
        return bot.say("Nothing to calculate.")
    eqn = trigger.group(2).replace(',', '.')
    queue = deque(eqn.split(None))
    stack = []
    operators = ['+', '-', '−', '*', '×', 'x', 'X', '/', '**', '//', '^', '!']
    while len(queue) > 0:
        symbol = queue.popleft()
        try:
            if symbol == 'e':
                stack.append(math.e)
            elif symbol == 'pi' or symbol == 'π':
                stack.append(math.pi)
            else:
                value = float(symbol)
                if value.is_integer():
                    stack.append(int(value))
                else:
                    stack.append(float(symbol))
        except ValueError:
            if symbol not in operators:
                bot.say("Unknown symbol: {}".format(symbol))
                return

            if symbol == '!':
                if len(stack) == 0:
                    bot.say("Error: operator without value!")
                    return
                num = stack.pop()
                if not isinstance(num, int):
                    bot.say("Factorial is only defined for integers.")
                    return
                stack.append(math.factorial(num))
                continue
            elif len(stack) < 2:
                bot.say('Too few values for operator {0}: {1}'
                        .format(symbol, stack))
                return
            else:
                val2 = stack.pop()
                val1 = stack.pop()

            if symbol == '+':
                result = val1 + val2

            elif symbol == '-' or symbol == '−':
                result = val1 - val2

            elif symbol in ['*', '×', 'x', 'X']:
                result = val1 * val2

            elif symbol == '^' or symbol == '**':
                result = math.pow(val1, val2)

            elif symbol == '/':
                result = val1 / val2

            elif symbol == '//':
                result = val1 // val2

            if isinstance(result, int) or result.is_integer():
                stack.append(int(result))
            else:
                stack.append(result)

    if len(stack) is not 1:
        bot.say("Error: values still on stack: {0}".format(stack))
    else:
        bot.say('{0}'.format(stack.pop()))


@commands('c', 'calc')
@example('.c 5 + 3', '8')
@example('.c 0.9*10', '9')
@example('.c 10*0.9', '9')
@example('.c 2*(1+2)*3', '18')
@example('.c 2**10', '1024')
@example('.c 5 // 2', '2')
@example('.c 5 / 2', '2.5')
def c(bot, trigger):
    """Evaluate some calculation."""
    if not trigger.group(2):
        return bot.say("Nothing to calculate.")
    # Account for the silly non-Anglophones and their silly radix point.
    eqn = trigger.group(2).replace(',', '.')
    try:
        result = eval_equation(eqn)
        result = "{:.10g}".format(result)
    except ZeroDivisionError:
        result = "Division by zero is not supported in this universe."
    except Exception as e:
        result = "{error}: {msg}".format(error=type(e), msg=e)
    bot.say(result)


@commands('py')
@example('.py len([1,2,3])', '3')
def py(bot, trigger):
    """Evaluate a Python expression."""
    if not trigger.group(2):
        return bot.say("Need an expression to evaluate")

    query = trigger.group(2)
    uri = BASE_TUMBOLIA_URI + 'py/'
    answer = requests.get(uri + quote(query)).text
    if answer:
        # bot.say can potentially lead to 3rd party commands triggering.
        bot.reply(answer)
    else:
        bot.reply('Sorry, no result.')


if __name__ == "__main__":
    from sopel.test_tools import run_example_tests
    run_example_tests(__file__)
