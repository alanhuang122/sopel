from sopel.module import commands
import threading

@commands('threads')
def threads_command(bot, trigger):
    for t in threading.enumerate():
        print(t.name)
