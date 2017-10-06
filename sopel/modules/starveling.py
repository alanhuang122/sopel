#!/usr/local/bin/python
#coding: latin-1

from sopel.module import commands
import random

phrases = ["Starveling Kitty! Starveling Kitty! Ruled the roofs of five stolen cities!",
        "the Starveling Cat! louder than a dog! taller than a rat!",
        "The Starveling Cat! The Starveling Cat! Swims like a bloodfish! Tastes like a sprat!",
        "The Starveling Cat! The Starveling Cat! Comes for the child who acts like a brat!",
        "the Starveling Cat! the Starveling Cat! it knows what we think! and we don't like that!",
        "the Starveling Cat! the Starveling Cat! mangy as a goat! mad as a bat!",
        "the Starveling Cat! the Starveling Cat! won't sit on a cushion! won't sit on a mat!",
        "the Starveling Cat! the Starveling Cat! want to lose a hand? give the beast a pat!",
        "The Sterveling Ket! The Sterveling Ket! What did it find in the oubliette?",
        "The Starveling Cat! The Starveling Cat! Wraps round your throat like a cheap cravat!",
        "the Starveling Cat! the Starveling Cat! look what it did! to your nice new hat!",
        "The Starveling Cat! The Starveling Cat! Jumped down the well for a good long chat!",
        "The Starveling Cat! The Starveling Cat! Sits on your chest when you're sleeping flat!",
        "The Starveling Cat! The Starveling Cat! Quick as a ratgun! Sharp as a gnat!",
        "The Starveling Cat! The Starveling Cat! Why does it look at us like that?",
        "the Starveling Cat! the Starveling Cat! stole your shoes! ate your cravat!",
        "the Starveling Cat! the Starveling Cat! warm as a lizard! fragrant as a bat!",
        "The Starveling Cat! The Starveling Cat! Sharp as ravenglass! Blunt as a bat!",
        "the Starveling Cat! the Starveling Cat! steals from your pantry! blames it on a rat!",
        "the Starveling Cat! the Starveling Cat! it likes your bones! it prefers your fat!"]

@commands('starveling')
def ket_command(bot, trigger):
    bot.say(random.choice(phrases))
