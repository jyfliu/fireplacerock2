import random

from callbacks import *

triggers = [
  # MANDATORY TURN EFFECTS
  "begin_phase_draw", # after turn player draws a card
  "begin_phase_standby", # "in your standby phase"
  "begin_phase_main", # "at the beginning of main phase"
  "end_phase_main", # "at the end of main phase"
  "begin_phase_battle", # "at the beginning of battle phase"
  "end_phase_battle", # "at the end of battle phase"
  "begin_phase_main_2", # "at the beginning of main phase 2"
  "end_phase_main_2", # "at the end of main phase 2"
  "begin_phase_end", # "in your end phase"
  # OPTIONAL TURN EFFCTS
  "opt_begin_phase_draw", # "in your draw phase you can"
  "opt_begin_phase_standby", # "in your standby phase you can"
  "opt_begin_phase_main", # "at the beginning of main phase you can"
  "opt_end_phase_main", # "at the end of main phase you can"
  "opt_begin_phase_battle", # "at the beginning of battle phase you can"
  "opt_end_phase_battle", # "at the end of battle phase you can"
  "opt_begin_phase_main_2", # "at the beginning of main phase 2 you can"
  "opt_end_phase_main_2", # "at the end of main phase 2 you can"
  "opt_end_phase_end", # "in your end phase you can"
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
  "on_activate_cost", # "you can ..." cost
  "on_activate", # "you can ..." effect
  # BATTLE EFFECTS
  "if_destroy_battle", # (other) if this destroys another by battle
  "if_destroyed_battle", # (other)
  "can_attack",
  "can_attack_directly",
  "if_attack", # if this monster is about to attack another monster
  "if_attack_directly", # if this monster is about to attack directly
  "if_attacked", # if this monster is selected for an attack
  "attacker_damage_calc", # (other) => attack damage done
  "attacker_direct_damage_calc", # (other) => attack damage done
  "attackee_damage_calc", # (other, amount) => attack damage done
  "defender_damage_calc", # (other) => recoil damage done
  "defendee_damage_calc", # (other, amount) => recoil damage done
  "on_take_damage", # if this monster takes damage
  "on_take_battle_damage", # if this monster takes damage from battle
  "end_attack", # (other, damage_dealt)
  "end_attacked", # (other, damage_dealt)
  # OPTIONAL BATTLE EFFECTS
  "opt_if_destroy_battle", # if this destroys another by battle
  "opt_if_destroyed_battle",
  "opt_if_attack", # if this monster is about to attack another monster
  "opt_if_attack_directly", # if this monster is about to attack directly
  "opt_if_attacked", # if this monster is selected for an attack
  "opt_end_attack", # (other, damage_dealt)
  "opt_end_attacked", # (other, damage_dealt)
  # SPELL EFFECTS
  "spell_can_activate",
  "spell_on_activate",
  "spell_on_resolve",
]

statuses = [
  "SILENCE",
  "PERISH",
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

    for fn in triggers:
      if hasattr(data, fn):
        script = getattr(data, fn)
        setattr(self, fn, script)
      else:
        continue


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

  def reset_stats(self):
    self.attack = self.original_attack
    self.health = self.original_health
    self.status = []

  def interp(self, script, *args):
    owner = self.owner
    other = self.other
    io = self.io

    field = owner.board + other.board

    prompt_user_activate = self.prompt_user_activate

    get_adjacent = self.get_adjacent
    # target empty space
    # returns idx into board (-1 if no space)
    # target_owner_board_empty = self.target_self_board_empty
    # target_other_board_empty = self.target_other_board_empty

    # target card on the field
    # optionally accepts a lambda to filter
    # returns card of monster
    can_target_field = self.can_target_field
    target_field = self.target_field
    can_target_owner_field = self.can_target_owner_field
    target_owner_field = self.target_owner_field
    can_target_other_field = self.can_target_other_field
    target_other_field = self.target_other_field

    # select monster on the field
    # optionally accepts a lambda to filter
    # returns monster
    can_select_field = self.can_select_field
    select_field = self.select_field
    can_select_owner_field = self.can_select_owner_field
    select_owner_field = self.select_owner_field
    can_select_other_field = self.can_select_other_field
    select_other_field = self.select_other_field

    # select card from deck
    can_select_owner_deck = self.can_select_owner_deck
    select_owner_deck = self.select_owner_deck
    can_select_other_deck = self.can_select_other_deck
    select_other_deck = self.select_other_deck

    # select card from deck
    # optionally accepts a lambda to filter
    # returns card
    # select_owner_deck = self.select_owner_deck
    # select_other_deck = self.select_other_deck

    # select card from gy
    can_select_owner_graveyard = self.can_select_owner_graveyard
    select_owner_graveyard = self.select_owner_graveyard
    can_select_other_graveyard = self.can_select_other_graveyard
    select_other_graveyard = self.select_other_graveyard

    # select empty spot
    can_select_owner_board = self.can_select_owner_board
    select_owner_board = self.select_owner_board
    can_select_other_board = self.can_select_other_board
    select_other_board = self.select_other_board

    flip_coin = self.flip_coin

    try:
      ldict = {}
      exec(script, globals() | locals(), ldict)
      if "retval" in ldict:
        return ldict["retval"]
      else:
        return
    except InvalidMove as e:
      print(e)
      pass

  ### IO ###

  def prompt_user_activate(self):
    return self.owner.io.prompt_user_activate(self.name)

  def select_cards(self, filter=lambda x: True):
    cards = [
        ("field", card)
        for card in self.owner.board
        if card is not None and filter(card)
    ] + [
        ("hand", card)
        for card in self.owner.hand
        if card is not None and filter(card)
    ] + [
        ("deck", card)
        for card in self.owner.deck
        if card is not None and filter(card)
    ] + [
        ("graveyard", card)
        for card in self.owner.graveyard
        if card is not None and filter(card)
    ] + [
        ("banished", card)
        for card in self.owner.banished
        if card is not None and filter(card)
    ] + [
        ("other_field", card)
        for card in self.other.board
        if card is not None and filter(card)
    ] + [
        ("other_hand", card)
        for card in self.other.hand
        if card is not None and filter(card)
    ] + [
        ("other_deck", card)
        for card in self.other.deck
        if card is not None and filter(card)
    ] + [
        ("other_graveyard", card)
        for card in self.other.graveyard
        if card is not None and filter(card)
    ] + [
        ("other_banished", card)
        for card in self.other.banished
        if card is not None and filter(card)
    ]
    return cards


  def can_select(self, filter=lambda x: True):
    return len(self.select_cards(filter)) > 0

  def select(self, filter=lambda x: True):
    if self.can_select(filter):
      cards = self.select_cards(filter)
      assert len(cards) > 0
      idx = self.owner.io.prompt_user_select(cards)

      _, card = cards[idx]
      return card
    else:
      raise InvalidMove("No valid targets")


  def can_target_owner_field(self, filter=lambda x: True):
    return self.can_select(lambda x: x in self.owner.board and filter(x))

  def target_owner_field(self, filter=lambda x: True):
    return self.select(lambda x: x in self.owner.board and filter(x))

  def can_target_other_field(self, filter=lambda x: True):
    return self.can_select(lambda x: x in self.other.board and filter(x))

  def target_other_field(self, filter=lambda x: True):
    return self.select(lambda x: x in self.other.board and filter(x))

  def can_target_field(self, filter=lambda x: True):
    return self.can_select(lambda x: (x in self.other.board or x in self.owner.board) and filter(x))

  def target_field(self, filter=lambda x: True):
    return self.select(lambda x: (x in self.other.board or x in self.owner.board) and filter(x))

  def can_select_owner_field(self, filter=lambda x: True):
    return self.can_select(lambda x: x in self.owner.board and filter(x))

  def select_owner_field(self, filter=lambda x: True):
    return self.select(lambda x: x in self.owner.board and filter(x))

  def can_select_other_field(self, filter=lambda x: True):
    return self.can_select(lambda x: x in self.other.board and filter(x))

  def select_other_field(self, filter=lambda x: True):
    return self.select(lambda x: x in self.other.board and filter(x))

  def can_select_field(self, filter=lambda x: True):
    return self.can_select(lambda x: (x in self.other.board or x in self.owner.board) and filter(x))

  def select_field(self, filter=lambda x: True):
    return self.select(lambda x: (x in self.other.board or x in self.owner.board) and filter(x))

  def can_select_owner_deck(self, filter=lambda x: True):
    return self.can_select(lambda x: x in self.owner.deck and filter(x))

  def select_owner_deck(self, filter=lambda x: True):
    return self.select(lambda x: x in self.owner.deck and filter(x))

  def can_select_other_deck(self, filter=lambda x: True):
    return self.can_select(lambda x: x in self.other.deck and filter(x))

  def select_other_deck(self, filter=lambda x: True):
    return self.select(lambda x: x in self.other.deck and filter(x))

  def can_select_owner_graveyard(self, filter=lambda x: True):
    return self.can_select(lambda x: x in self.owner.graveyard and filter(x))

  def select_owner_graveyard(self, filter=lambda x: True):
    return self.select(lambda x: x in self.owner.graveyard and filter(x))

  def can_select_other_graveyard(self, filter=lambda x: True):
    return self.can_select(lambda x: x in self.other.graveyard and filter(x))

  def select_other_graveyard(self, filter=lambda x: True):
    return self.select(lambda x: x in self.other.graveyard and filter(x))

  def can_select_owner_board(self):
    return None in self.owner.board

  def select_owner_board(self):
    nums = []
    for i, card in enumerate(self.owner.board):
      if card is None:
        nums.append(i)
    idx = self.owner.io.prompt_user_select_board(nums)
    return idx

  def can_select_other_board(self):
    return None in self.other.board

  def select_other_board(self):
    nums = []
    for i, card in enumerate(self.other.board):
      if card is None:
        nums.append(i)
    idx = self.owner.io.prompt_user_select_board(nums)
    return idx

  def flip_coin(self):
    coin = random.randint(0, 1)
    self.owner.io.flip_coin(coin)
    self.other.io.flip_coin(coin)
    return coin

  def get_adjacent(self):
    for i, c in enumerate(self.owner.board):
      if c == self:
        break
    else: # for else
      return []

    adjs = []
    if i > 0 and self.owner.board[i - 1]:
      adjs.append(self.owner.board[i - 1])
    if i < len(self.owner.board) - 1 and self.owner.board[i + 1]:
      adjs.append(self.owner.board[i + 1])

    return adjs

  ### STATUS ###
  # SILENCE
  # UNTARGETABLE
  #

  def has_status(self, status):
    for st in self.status:
      if st[0] == status:
        return True
    return False

  def apply_status(self, source, status, duration=0, expiry="end"):
    self.status.append([status, duration, expiry])

  def on_end_turn(self):
    new_status = []
    for st in self.status:
      if st[1] < 0:
        new_status.append(st)
      elif st[1] == 0:
        if st[0] == "PERISH":
          self.io.destroy(self)
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
      if source == "battle":
        self.effect("on_take_battle_damage")
      self.effect("on_take_damage", amount)
      self.health -= amount

  def set(self, source, attack=None, health=None):
    if attack is not None:
      self.attack = attack
    if health is not None:
      self.health = health

  def effect(self, trigger, *args):
    if hasattr(self.template, trigger):
      print(f"{self.name} activates its effect {trigger}")
      return self.interp(getattr(self.template, trigger), *args)
    else:
      return self.default(trigger, *args)

  def can(self, action, *args):
    """
    action in ["attack", "summon", "target", "activate"]
    todo: implement source (eg., is it a monster or spell targeting)
    """

    trigger = f"can_{action}"
    if hasattr(self.template, trigger):
      return self.interp(getattr(self.template, trigger), *args)
    else:
      return self.default(trigger, *args)

  def default(self, trigger, *args):
    if trigger == "can_summon":
      return True
    elif trigger == "can_attack":
      return not self.has_status("CANNOT_ATTACK")
    elif trigger == "can_activate":
      return (
        hasattr(self.template, "on_activate")
        and not self.has_status("SILENCE")
      )
    elif trigger == "can_attack_directly":
      return not self.has_status("CANNOT_ATTACK")
    elif trigger == "can_target":
      return not self.has_status("UNTARGETABLE")
    elif trigger == "attacker_damage_calc":
      return self.attack
    elif trigger == "attacker_direct_damage_calc":
      return self.attack
    elif trigger == "attackee_damage_calc":
      other, amount = args
      return amount
    elif trigger == "defender_damage_calc":
      return self.attack
    elif trigger == "defendee_damage_calc":
      other, amount = args
      return amount
    elif "opt" in trigger and "cost" in trigger:
      return hasattr(self.template, trigger[:-5]) and self.io.prompt_user_activate(self.name)
    elif "cost" in trigger:
      return True
    else:
      return

  def __str__(self):
    if self.type == "monster":
      return f"{self.name} {self.cost} {self.attack}/{self.health}"
    else:
      return f"{self.name} {self.cost}"


