import pygame
import random

from callbacks import *

functions = [
  "on_summon",
  "on_destroy",
  "on_send_graveyard",
  "on_attack",
  "on_attack_directly",
  "on_attacked",
]

class Template:

  def __init__(self, data):
    self.name = data.name
    self.mana = data.mana
    self.attack = data.attack
    self.health = data.health
    self.description = data.description

    for fn in functions:
      if hasattr(data, fn):
        script = getattr(data, fn)
      else:
        script = setattr(self, fn, "")
        continue
      setattr(self, fn, script)


  def create_instance(self, owner, other, io):
    return Card(self, owner, other, io)


class Card:

  def __init__(self, template, owner, other, io):
    self.template = template
    self.name = self.template.name
    self.mana = template.mana
    self.attack = template.attack
    self.health = template.health
    self.status = []

    self.owner = owner
    self.other = other
    self.io = io

    self.kwargs = {
        "self": self,
        "owner": owner,
        "other": other,
        "io": io,
    }

  def interp(self, script, *args):
    target_other_field = self.io.target_other_field
    try:
      exec(script)
    except InvalidMove as e:
      print(e)
      pass

  def on_summon(self):
    print(f"{self.name} is summoned")
    self.interp(self.template.on_summon)

  def on_destroy(self):
    print(f"{self.name} is destroyed")
    self.interp(self.template.on_destroy)

  def on_send_graveyard(self):
    self.interp(self.template.on_send_graveyard)

  def on_attack(self, other):
    print(f"{self.name} attacks {other.template.name}")
    self.interp(self.template.on_attack, other)

  def on_attack_directly(self):
    print(f"{self.name} attacks directly")
    self.interp(self.template.on_attack_directly)

  def on_attacked(self, other):
    self.interp(self.template.on_attack)

  def __str__(self):
    return f"{self.name} {self.mana} {self.attack}/{self.health}"


