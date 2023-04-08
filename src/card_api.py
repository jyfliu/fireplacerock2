import pygame
import random

from callbacks import *

triggers = [
  # MANDATORY TURN EFFECTS
  "on_draw_phase", # after turn player draws a card
  "on_standby_phase", # "in your standby phase"
  "begin_main_phase", # "at the beginning of main phase"
  "end_main_phase", # "at the end of main phase"
  "begin_battle_phase", # "at the beginning of battle phase"
  "end_battle_phase", # "at the end of battle phase"
  "begin_main_phase_2", # "at the beginning of main phase 2"
  "end_main_phase_2", # "at the end of main phase 2"
  "on_end_phase", # "in your end phase"
  # OPTIONAL TURN EFFCTS
  "opt_on_draw_phase", # "in your draw phase you can"
  "opt_on_standby_phase", # "in your standby phase you can"
  "opt_begin_main_phase", # "at the beginning of main phase you can"
  "opt_end_main_phase", # "at the end of main phase you can"
  "opt_begin_battle_phase", # "at the beginning of battle phase you can"
  "opt_end_battle_phase", # "at the end of battle phase you can"
  "opt_begin_main_phase_2", # "at the beginning of main phase 2 you can"
  "opt_end_main_phase_2", # "at the end of main phase 2 you can"
  "opt_on_end_phase", # "in your end phase you can"
  # CARD EFFECTS
  "can_summon",
  "on_summon", # summoning conditions (eg., tribute), doesn't start chain
  "if_summon_cost", # "if this card is summoned" cost
  "if_summon", # "if this card is summoned" effect
  "if_destroyed", # "if this card is destroyed"
  "if_send_graveyard", # "if this card is sent to the graveyard"
  # OPTIONAL CARD EFFECTS
  "opt_if_summon_cost", # "if this card is summoned" cost
  "opt_if_summon", # "if this card is summoned" effect
  "opt_if_destroyed", # "if this card is destroyed"
  "opt_if_send_graveyard", # "if this card is sent to the graveyard"
  "can_activate",
  "on_activate", # "you can ..."
  # BATTLE EFFECTS
  "if_destroy_battle", # if this destroys another by battle
  "if_destroyed_battle",
  "can_attack",
  "if_attack", # if this monster is about to attack another monster
  "if_attack_directly", # if this monster is about to attack directly
  "if_attacked", # if this monster is selected for an attack
  "attacker_damage_calc", # (other) => attack damage done
  "attackee_damage_calc", # (other, amount) => attack damage done
  "if_take_damage", # if this monster takes damage
  "if_take_battle_damage", # if this monster takes damage from battle
  "end_attack",
  "end_attacked",
  # OPTIONAL BATTLE EFFECTS
  "opt_if_destroy_battle", # if this destroys another by battle
  "opt_if_destroyed_battle",
  "opt_if_attack", # if this monster is about to attack another monster
  "opt_if_attack_directly", # if this monster is about to attack directly
  "opt_if_attacked", # if this monster is selected for an attack
  "opt_if_take_damage", # if this monster takes damage
  "opt_if_take_battle_damage", # if this monster takes damage from battle
  "opt_end_attack",
  "opt_end_attacked",
  # SPELL EFFECTS
  "spell_can_activate",
  "spell_on_activate",
  "spell_on_resolve",
]

statuses = [
  "SILENCE",
]

class Template:

  def __init__(self, data):
    self.name = data.name
    self.cost = data.cost
    self.type = data.type
    if self.type == "monster":
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
    self.name = template.name
    self.cost = template.cost
    self.type = template.type
    if self.type == "monster":
      self.attack = template.attack
      self.health = template.health
      self.original_attack = template.attack
      self.original_health = template.health
    self.status = []

    self.owner = owner
    self.other = other
    self.io = io

  def interp(self, script, *args):
    owner = self.owner
    other = self.other
    io = self.io

    field = owner.board + other.board

    get_adjacent = self.io.get_adjacent
    # target empty space
    # returns idx into board (-1 if no space)
    target_owner_board_empty = self.io.target_owner_board_empty
    target_other_board_empty = self.io.target_other_board_empty

    # target card on the field
    # optionally accepts a lambda to filter
    # returns card of monster
    target_field = self.io.target_field
    target_owner_field = self.io.target_owner_field
    target_other_field = self.io.target_other_field

    # select monster on the field
    # optionally accepts a lambda to filter
    # returns monster
    select_field = self.io.select_field
    select_owner_field = self.io.select_owner_field
    select_other_field = self.io.select_other_field

    # select card from deck
    # optionally accepts a lambda to filter
    # returns card
    select_owner_deck = self.io.select_owner_deck
    # select_other_deck = self.io.select_other_deck

    # select card from deck
    # optionally accepts a lambda to filter
    # returns card
    select_owner_graveyard = self.io.select_owner_graveyard
    select_other_graveyard = self.io.select_other_graveyard

    flip_coin = self.io.flip_coin

    try:
      exec(script)
    except InvalidMove as e:
      print(e)
      pass

  ### STATUS ###

  def has_status(self, status):
    for st in self.status:
      if st[0] == status:
        return True
    return False

  def apply_status(self, source, status, duration=0, expiry="end"):
    self.status.append((status, duration, expiry))

  def end_turn(self):
    new_status = []
    for st in self.status:
      if st[1] < 0:
        new_status.append(st)
      elif st[1] == 0:
        pass # expire status (NEED TO CHECK WHAT STGE IT IS!!)
      else:
        st[1] = st[1] - 1
        new_status.append(st)
    self.status = new_status

  ### HELPERS ###
  def heal(self, source, amount):
    # self.on_heal(amount)
    if self.health <= self.original_health - amount:
      self.health += amount
    elif self.health <= self.original_health:
      self.health = self.original_health
    else:
      pass

  def gain(self, source, attack=0, health=0):
    # source = [f]
    self.attack += attack
    self.health += health

  def lose(self, source, attack=0, health=0):
    # todo self.on_lose_attack?
    self.attack -= attack
    self.health -= health

  def take_damage(self, source, amount):
    if amount > 0:
      amount = self.on_take_damage(amount)
      self.health -= amount


  def set(self, source, attack=0, health=0):
    pass

  def try_activate_effect(self, trigger, *args):
    try:
      return self.interp(getattr(self.template, trigger), *args)
    except:
      return self.default(trigger)

  def can(self, trigger, *args):
    try:
      return self.interp(getattr(self.template, trigger), *args)
    except:
      return self.default(trigger, *args)

  def default(self, trigger, *args):
    if trigger == "can_summon":
      return True
    elif trigger == "can_attack":
      return not self.has_status("CANNOT_ATTACK")
    elif trigger == "attacker_damage_calc":
      return self.attack
    elif trigger == "attackee_damage_calc":
      other, amount = args
      return amount
    else:
      return

  def __str__(self):
    return f"{self.name} {self.cost} {self.attack}/{self.health}"


