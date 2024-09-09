import os
import matplotlib.pyplot as plt
import base64
import random
import itertools

from .callbacks import *
from . import archetypes

triggers = [
  # MANDATORY TURN EFFECTS
  "begin_phase_draw", # after turn player draws a card
  "begin_phase_standby", # "in the standby phase"
  "begin_phase_main", # "at the beginning of main phase"
  "end_phase_main", # "at the end of each main phase"
  "begin_phase_battle", # "at the beginning of each battle phase"
  "end_phase_battle", # "at the end of each battle phase"
  "begin_phase_main_2", # "at the beginning of each main phase 2"
  "end_phase_main_2", # "at the end of each main phase 2"
  "begin_phase_end", # "in your end phase"
  # OPTIONAL TURN EFFCTS
  "opt_begin_phase_draw", # "in each draw phase you can"
  "opt_begin_phase_standby", # "in each standby phase you can"
  "opt_begin_phase_main", # "at the beginning of main phase you can"
  "opt_end_phase_main", # "at the end of main phase you can"
  "opt_begin_phase_battle", # "at the beginning of battle phase you can"
  "opt_end_phase_battle", # "at the end of battle phase you can"
  "opt_begin_phase_main_2", # "at the beginning of main phase 2 you can"
  "opt_end_phase_main_2", # "at the end of main phase 2 you can"
  "opt_end_phase_end", # "in your end phase you can"
  # MANDATORY TURN EFFECTS
  "begin_phase_your_draw", # after turn player draws a card
  "begin_phase_your_standby", # "in the standby phase"
  "begin_phase_your_main", # "at the beginning of main phase"
  "end_phase_your_main", # "at the end of each main phase"
  "begin_phase_your_battle", # "at the beginning of each battle phase"
  "end_phase_your_battle", # "at the end of each battle phase"
  "begin_phase_your_main_2", # "at the beginning of each main phase 2"
  "end_phase_your_main_2", # "at the end of each main phase 2"
  "begin_phase_your_end", # "in your end phase"
  # OPTIONAL TURN EFFCTS
  "opt_begin_phase_your_draw", # "in each draw phase you can"
  "opt_begin_phase_your_standby", # "in each standby phase you can"
  "opt_begin_phase_your_main", # "at the beginning of main phase you can"
  "opt_end_phase_your_main", # "at the end of main phase you can"
  "opt_begin_phase_your_battle", # "at the beginning of battle phase you can"
  "opt_end_phase_your_battle", # "at the end of battle phase you can"
  "opt_begin_phase_your_main_2", # "at the beginning of main phase 2 you can"
  "opt_end_phase_your_main_2", # "at the end of main phase 2 you can"
  "opt_end_phase_your_end", # "in your end phase you can"
  # CARD EFFECTS
  "can_summon",
  "on_summon", # summoning conditions (eg., tribute), doesn't start chain, TODO rename this?
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
  "can_activate_hand",
  "on_activate_hand_cost",
  "on_activate_hand",
  # extra deck
  "can_summon_extradeck",
  "summon_extradeck",
  # movement
  "on_remove", # remove from field
]
# hooks are triggers that require event listeners on other cards
hooks = [
  "on_owner_summon",
  "on_owner_remove",
  "on_owner_destroyed",
  "on_owner_send_graveyard",
  "on_owner_pay_mana",
  "on_oppon_summon",
  "on_oppon_remove",
  "on_oppon_destroyed",
  "on_oppon_send_graveyard",
  "on_oppon_pay_mana",
]
triggers += hooks

statuses = [
  "UNTARGETABLE",
  "SILENCE",
  "PERISH",
  "BANISH",
  "WEAKEN",
  "STRENGTHEN",
  "TRANSFORMED",
]

class SpriteCache:

  def __init__(self):
    self.sprites = {}
    self.rgb = {}

  def load(self, path):
    if path not in self.sprites:
      print(f"READ {path}")
      with open(path, "rb") as f:
        self.sprites[path] = base64.b64encode(f.read()).decode("utf-8")
      r, g, b = plt.imread(path).mean(axis=0).mean(axis=0)
      self.rgb[path] = [r, g, b]
    return self.sprites[path], self.rgb[path]

class Template:

  cache = SpriteCache()

  def __init__(self, data):
    self.set, self.print = data.id.split(":")

    self.id = data.uuid
    self.name = data.name
    self.cost = data.cost
    self.type = data.type
    if self.type == "monster":
      self.attack = data.attack
      self.health = data.health
    self.description = data.description
    if hasattr(data, "flavour"):
      self.flavour = data.flavour
    else:
      self.flavour = ""

    for fn in triggers:
      if hasattr(data, fn):
        script = getattr(data, fn)
        setattr(self, fn, script)
      else:
        continue

    sprite_path = f"../res/cards/{self.set}/{self.id}.jpg"
    sprite_mini_path = f"../res/cards/{self.set}/{self.id}.mini.jpg"
    self.mini_sprite = None
    self.sprite = None
    if os.path.exists(sprite_path):
      self.sprite, self.bkgd_colour = Template.cache.load(sprite_path)
    elif os.path.exists(sprite_mini_path):
      self.mini_sprite, self.bkgd_colour = Template.cache.load(sprite_mini_path)
    else:
      r, g, b = 255, 255, 255
      self.bkgd_colour = [r, g, b]


  def create_instance(self, owner, oppon, io):
    return Card(self, owner, oppon, io)


class God:
  def __init__(self):
    self.uuid = -1
    self.name = "god"
  def has_status(self, *args, **kwargs):
    return False
god = God()


class Card:

  last_uuid = 0

  def __init__(self, template, owner, oppon, io):
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
    self.oppon = oppon
    self.io = io

    Card.last_uuid += 1
    self.uuid = Card.last_uuid

    self.id = self.template.id


  def __eq__(self, other):
    if other is None:
      return False
    return self.uuid == other.uuid


  def reset_stats(self):
    if self.type == "monster":
      self.attack = self.original_attack
      self.health = self.original_health
      self.owner.io.card_set(self.uuid, None, self.original_attack, self.original_health)
      self.oppon.io.card_set(self.uuid, None, self.original_attack, self.original_health)
    self.status = []

  def interp(self, script, *args):
    owner = self.owner
    oppon = self.oppon
    io = self.io

    field = owner.field + oppon.field
    all_cards = (
        owner.field + oppon.field
        + owner.deck + oppon.deck
        + owner.extradeck + oppon.extradeck
        + owner.graveyard + oppon.graveyard
        + owner.banished + oppon.banished
        + owner.hand + oppon.hand
    )

    prompt_user_activate = self.prompt_user_activate

    get_current_board_idx = self.get_current_board_idx
    get_adjacent_board_idxs = self.get_adjacent_board_idxs
    get_adjacent = self.get_adjacent
    get_opposing = self.get_opposing
    get_opposing_adjacent = self.get_opposing_adjacent

    # target card on the field
    # optionally accepts a lambda to filter
    # returns card of monster
    can_target_field = self.can_target_field
    target_field = self.target_field
    can_target_owner_field = self.can_target_owner_field
    target_owner_field = self.target_owner_field
    can_target_oppon_field = self.can_target_oppon_field
    target_oppon_field = self.target_oppon_field
    can_target_owner_traps = self.can_target_owner_traps
    target_owner_traps = self.target_owner_traps
    can_target_oppon_traps = self.can_target_oppon_traps
    target_oppon_traps = self.target_oppon_traps

    can_select = self.can_select
    select = self.select

    # select monster on the field
    # optionally accepts a lambda to filter
    # returns monster
    can_select_field = self.can_select_field
    select_field = self.select_field
    can_select_owner_field = self.can_select_owner_field
    select_owner_field = self.select_owner_field
    can_select_oppon_field = self.can_select_oppon_field
    select_oppon_field = self.select_oppon_field

    can_select_traps = self.can_select_traps
    select_traps = self.select_traps
    can_select_owner_traps = self.can_select_owner_traps
    select_owner_traps = self.select_owner_traps
    can_select_oppon_traps = self.can_select_oppon_traps
    select_oppon_traps = self.select_oppon_traps

    # select card from deck
    can_select_owner_deck = self.can_select_owner_deck
    select_owner_deck = self.select_owner_deck
    can_select_oppon_deck = self.can_select_oppon_deck
    select_oppon_deck = self.select_oppon_deck

    can_select_owner_extradeck = self.can_select_owner_extradeck
    select_owner_extradeck = self.select_owner_extradeck
    can_select_oppon_extradeck = self.can_select_oppon_extradeck
    select_oppon_extradeck = self.select_oppon_extradeck

    # select card from deck
    # optionally accepts a lambda to filter
    # returns card
    # select_owner_deck = self.select_owner_deck
    # select_oppon_deck = self.select_oppon_deck

    # select card from gy
    can_select_owner_graveyard = self.can_select_owner_graveyard
    select_owner_graveyard = self.select_owner_graveyard
    can_select_oppon_graveyard = self.can_select_oppon_graveyard
    select_oppon_graveyard = self.select_oppon_graveyard
    can_select_graveyard = self.can_select_graveyard
    select_graveyard = self.select_graveyard

    # select empty spot
    can_select_owner_board = self.can_select_owner_board
    select_owner_board = self.select_owner_board
    can_select_oppon_board = self.can_select_oppon_board
    select_oppon_board = self.select_oppon_board

    # extra deck
    can_link = self.can_link
    link = self.link

    # misc
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
    except e:
      print(e)
      raise

  ### IO ###

  def prompt_user_activate(self):
    return self.owner.io.prompt_user_activate(self.name)

  def select_cards(self, filter=lambda x: True):
    cards = [
        ("field", card)
        for card in self.owner.board
        if card is not None and filter(card)
    ] + [
        ("spells", card)
        for card in self.owner.traps
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
        ("extradeck", card)
        for card in self.owner.extradeck
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
        ("oppon_field", card)
        for card in self.oppon.board
        if card is not None and filter(card)
    ] + [
        ("oppon_spells", card)
        for card in self.oppon.traps
        if card is not None and filter(card)
    ] + [
        ("oppon_hand", card)
        for card in self.oppon.hand
        if card is not None and filter(card)
    ] + [
        ("oppon_deck", card)
        for card in self.oppon.deck
        if card is not None and filter(card)
    ] + [
        ("oppon_extradeck", card)
        for card in self.oppon.extradeck
        if card is not None and filter(card)
    ] + [
        ("oppon_graveyard", card)
        for card in self.oppon.graveyard
        if card is not None and filter(card)
    ] + [
        ("oppon_banished", card)
        for card in self.oppon.banished
        if card is not None and filter(card)
    ]
    return cards


  def can_select(self, filter=lambda x: True, amount=1):
    return len(self.select_cards(filter)) >= amount

  def select(self, filter=lambda x: True, amount=1):
    if self.can_select(filter):
      cards = self.select_cards(filter)
      assert len(cards) > 0
      idx = self.owner.io.prompt_user_select(cards, amount=amount)
      if amount == 1:
        _, card = cards[idx[0]]
        return card
      else:
        retval = []
        for i in idx:
          _, card = cards[i]
          retval.append(card)
        return retval
    else:
      raise InvalidMove("No valid targets")

  def can_target(self, other):
    if self.type == "monster" or self.type == "boss monster":
      return other.can("can_target_monster")
    elif self.type == "spell" or self.type == "field spell":
      return other.can("can_target_spell")
    else:
      return False

  def can_target_owner_field(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: x in self.owner.board and filter(x) and can_target(other), amount=amount)

  def target_owner_field(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: x in self.owner.board and filter(x), amount=amount)

  def can_target_oppon_field(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: x in self.oppon.board and filter(x), amount=amount)

  def target_oppon_field(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: x in self.oppon.board and filter(x), amount=amount)

  def can_target_field(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: (x in self.oppon.board or x in self.owner.board) and filter(x), amount=amount)

  def target_field(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: (x in self.oppon.board or x in self.owner.board) and filter(x), amount=amount)

  def can_select_owner_field(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: x in self.owner.board and filter(x), amount=amount)

  def select_owner_field(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: x in self.owner.board and filter(x), amount=amount)

  def can_select_oppon_field(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: x in self.oppon.board and filter(x), amount=amount)

  def select_oppon_field(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: x in self.oppon.board and filter(x), amount=amount)

  def can_select_field(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: (x in self.oppon.board or x in self.owner.board) and filter(x), amount=amount)

  def select_field(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: (x in self.oppon.board or x in self.owner.board) and filter(x), amount=amount)

  def can_target_owner_traps(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: x in self.owner.traps and filter(x) and can_target(other), amount=amount)

  def target_owner_traps(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: x in self.owner.traps and filter(x), amount=amount)

  def can_target_oppon_traps(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: x in self.oppon.traps and filter(x), amount=amount)

  def target_oppon_traps(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: x in self.oppon.traps and filter(x), amount=amount)

  def can_target_traps(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: (x in self.oppon.traps or x in self.owner.traps) and filter(x), amount=amount)

  def target_traps(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: (x in self.oppon.traps or x in self.owner.traps) and filter(x), amount=amount)

  def can_select_owner_traps(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: x in self.owner.traps and filter(x), amount=amount)

  def select_owner_traps(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: x in self.owner.traps and filter(x), amount=amount)

  def can_select_oppon_traps(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: x in self.oppon.traps and filter(x), amount=amount)

  def select_oppon_traps(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: x in self.oppon.traps and filter(x), amount=amount)

  def can_select_traps(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: (x in self.oppon.traps or x in self.owner.traps) and filter(x), amount=amount)

  def select_traps(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: (x in self.oppon.traps or x in self.owner.traps) and filter(x), amount=amount)

  def can_select_owner_deck(self, filter=lambda x: True, amount=1):
    retval = self.can_select(lambda x: x in self.owner.deck and filter(x), amount=amount)
    return retval

  def select_owner_deck(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: x in self.owner.deck and filter(x), amount=amount)

  def can_select_owner_extradeck(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: x in self.owner.extradeck and filter(x), amount=amount)

  def select_owner_extradeck(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: x in self.owner.extradeck and filter(x), amount=amount)

  def can_select_oppon_deck(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: x in self.oppon.deck and filter(x), amount=amount)

  def select_oppon_deck(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: x in self.oppon.deck and filter(x), amount=amount)

  def can_select_oppon_extradeck(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: x in self.oppon.extradeck and filter(x), amount=amount)

  def select_oppon_extradeck(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: x in self.oppon.extradeck and filter(x), amount=amount)

  def can_select_owner_graveyard(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: x in self.owner.graveyard and filter(x), amount=amount)

  def select_owner_graveyard(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: x in self.owner.graveyard and filter(x), amount=amount)

  def can_select_oppon_graveyard(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: x in self.oppon.graveyard and filter(x), amount=amount)

  def select_oppon_graveyard(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: x in self.oppon.graveyard and filter(x), amount=amount)

  def can_select_graveyard(self, filter=lambda x: True, amount=1):
    return self.can_select(lambda x: (x in self.owner.graveyard or x in self.oppon.graveyard) and filter(x), amount=amount)

  def select_graveyard(self, filter=lambda x: True, amount=1):
    return self.select(lambda x: (x in self.owner.graveyard or x in self.oppon.graveyard) and filter(x), amount=amount)

  def can_select_owner_board(self, idxs=None):
    if not idxs:
      return None in self.owner.board
    else:
      return any(self.owner.board[i] is None for i in idxs)

  def select_owner_board(self, idxs=None):
    if idxs is None:
      idxs = range(len(self.owner.board))
    nums = []
    for i, card in enumerate(self.owner.board):
      if card is None and i in idxs:
        nums.append(i)
    idx = self.owner.io.prompt_user_select_board(nums)
    return idx

  def can_select_oppon_board(self):
    return None in self.oppon.board

  def select_oppon_board(self):
    nums = []
    for i, card in enumerate(self.oppon.board):
      if card is None:
        nums.append(i)
    idx = self.owner.io.prompt_user_select_board(nums)
    return idx

  def link_satisfies_requirements(self, cards, reqs):
    if len(cards) != len(reqs):
      return False
    for try_cards in itertools.permutations(cards):
      success = all(req(card) for card, req in zip(try_cards, reqs))
      if success:
        return True
    return False

  def can_link(self, *reqs):
    if not self.owner.can_pay(self.cost):
      return False
    for cards in itertools.combinations(self.owner.field, len(reqs)):
      if self.link_satisfies_requirements(cards, reqs):
        return True
    return False

  def link(self, *reqs):
    self.owner.pay(self.cost)

    cards = []
    for req in reqs:
      cards.append(self.select_owner_field(lambda card: card not in cards and req(card)))
    self.io.send_graveyard_multiple(cards)

  def flip_coin(self):
    coin = random.randint(0, 1)
    self.owner.io.flip_coin(coin)
    self.oppon.io.flip_coin(coin)
    return coin

  def get_current_board_idx(self):
    for i, c in enumerate(self.owner.board):
      if c == self:
        return i
    return -1

  def get_adjacent_board_idxs(self):
    i = self.get_current_board_idx()
    if i == -1:
      return []
    adjs = []
    if i > 0:
      adjs.append(i - 1)
    if i < len(self.owner.board) - 1:
      adjs.append(i + 1)
    return adjs

  def get_adjacent(self):
    adjs = self.get_adjacent_board_idxs()
    adjs = [self.owner.board[i] for i in adjs if self.owner.board[i] is not None]

    return adjs

  def get_opposing(self):
    # opposing card if exist
    board_idx = self.get_current_board_idx()
    if board_idx == -1:
      return []
    if self.oppon.board[board_idx] is not None:
      return [self.oppon.board[board_idx]]
    else:
      return []

  def get_opposing_adjacent(self):
    # adjacent to opposing if exist
    board_idx = self.get_current_board_idx()
    if board_idx == -1:
      return []
    results = []
    if board_idx > 0 and self.oppon.board[board_idx-1] is not None:
      results += [self.oppon.board[board_idx-1]]
    if board_idx < len(self.oppon.board) - 1 and self.oppon.board[board_idx+1] is not None:
      results += [self.oppon.board[board_idx+1]]
    return results


  def has_status(self, status):
    for st in self.status:
      if st[0] == status and not st[3].has_status("SILENCE"):
        return True
    return False

  def apply_status(self, source, status, duration=0, expiry="end", args=True):
    self.status.append([status, duration, expiry, source, args])
    self.owner.io.apply_status(self.uuid, status, duration, expiry, args)
    self.oppon.io.apply_status(self.uuid, status, duration, expiry, args)

  def clear_status(self, status, source=None):
    if source is None:
      self.status = [s for s in self.status if s[0] != status]
    else:
      self.status = [s for s in self.status if s[0] != status or s[3] != source]
    self.owner.io.clear_status(self.uuid, status)
    self.oppon.io.clear_status(self.uuid, status)

  def on_end_turn(self):
    new_status = []
    for st in self.status:
      status, duration, expiry, source, args = st
      if duration < 0:
        new_status.append(st)
      elif duration == 0:
        self.owner.io.clear_status(self.uuid, st[0])
        self.oppon.io.clear_status(self.uuid, st[0])
        if status == "PERISH":
          self.io.destroy(self)
        if status == "BANISH":
          self.io.banish(self)
        if status == "TRANSFORMED":
          self.template = args
        pass # expire status (NEED TO CHECK WHAT STGE IT IS!!)
      else:
        st[1] = duration - 1
        new_status.append(st)
    self.status = new_status

  ### HELPERS ###
  def change_name(self, new_name):
    self.name = new_name
    self.owner.io.card_change_name(self.uuid, new_name)
    self.oppon.io.card_change_name(self.uuid, new_name)

  def heal(self, source, amount):
    # self.on_heal(amount)
    if self.health <= self.original_health - amount:
      heal_amount = amount
    elif self.health <= self.original_health:
      heal_amount = self.original_health - self.health
    else:
      heal_amount = 0
    self.health += heal_amount
    self.owner.io.card_gain(self.uuid, None, 0, heal_amount)
    self.oppon.io.card_gain(self.uuid, None, 0, heal_amount)

  def gain(self, source, attack=0, health=0):
    # source = [f]
    self.attack += attack
    self.health += health
    self.owner.io.card_gain(self.uuid, None, attack, health)
    self.oppon.io.card_gain(self.uuid, None, attack, health)

  def original_gain(self, source, attack=0, health=0):
    # source = [f]
    self.attack += attack
    self.health += health
    self.original_attack += attack
    self.original_health += health
    self.owner.io.card_gain(self.uuid, None, attack, health)
    self.oppon.io.card_gain(self.uuid, None, attack, health)

  def lose(self, source, attack=0, health=0):
    # todo self.on_lose_attack?
    self.attack -= attack
    self.health -= health
    self.owner.io.card_lose(self.uuid, None, attack, health)
    self.oppon.io.card_lose(self.uuid, None, attack, health)

  def take_battle_damage(self, source, amount):
    if amount > 0:
      self.effect("on_take_battle_damage", amount)
      self.take_damage(source, amount)

  def take_damage(self, source, amount):
    if amount > 0:
      self.effect("on_take_damage", amount)
      self.health -= amount
      self.owner.io.card_take_damage(self.uuid, None, amount)
      self.oppon.io.card_take_damage(self.uuid, None, amount)

  def set(self, source, attack=None, health=None):
    if attack is not None:
      self.attack = attack
    else:
      attack = self.attack
    if health is not None:
      self.health = health
    else:
      health = self.health
    self.owner.io.card_set(self.uuid, None, attack, health)
    self.oppon.io.card_set(self.uuid, None, attack, health)

  def transform(self, template, duration, source, keep_stats=False):
    self.apply_status(self, source, "TRANSFORMED", duration=duration, args=self.template)
    self.template = template
    if not keep_stats:
      self.reset_stats()

  def add_hook(self, hook_name):
    script = getattr(self.template, hook_name)
    def hook_fn(card):
      self.owner.io.display_message(f"Your {self.name} activates its effect {hook_name}")
      self.oppon.io.display_message(f"Their {self.name} activates its effect {hook_name}")
      return self.interp(script, card)
    self.owner.hooks[hook_name].append((self, hook_fn))

  def add_hooks(self):
    for hook_name in hooks:
      if hasattr(self.template, hook_name):
        # print(f"{self.name} adds hook {hook_name}")
        self.add_hook(hook_name)

  def remove_hooks(self):
    for hook_name in hooks:
      if hasattr(self.template, hook_name):
        # has_hook = any([c == self for c, _ in self.owner.hooks[hook_name]])
        # if has_hook:
          # print(f"{self.name} removes hook {hook_name}")
        self.owner.hooks[hook_name] = [(c, h) for c, h in self.owner.hooks[hook_name] if c != self]

  def effect(self, trigger, *args, check_field=True):
    if hasattr(self.template, trigger):
      self.owner.io.display_message(f"Your {self.name} activates its effect {trigger}")
      self.oppon.io.display_message(f"Their {self.name} activates its effect {trigger}")
      retval = self.interp(getattr(self.template, trigger), *args)
      if check_field:
        self.io.check_field(self)
      return retval
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
      return self.type == "monster"
    if trigger == "can_summon_extradeck":
      return hasattr(self.template, "summon_extradeck")
    elif trigger == "can_attack":
      return not self.has_status("CANNOT_ATTACK")
    elif trigger == "can_activate":
      return (
        hasattr(self.template, "on_activate")
        and not self.has_status("SILENCE")
      )
    elif trigger == "can_activate_hand":
      return (
        hasattr(self.template, "on_activate_hand")
      )
    elif trigger == "can_attack_directly":
      return (
        not self.has_status("CANNOT_ATTACK")
        # if everything has taunt uncomment
        # and not len(self.oppon.field)
      )
    elif trigger == "can_target_monster":
      return not self.has_status("UNTARGETABLE") or not self.has_status("MONSTER_UNTARGETABLE")
    elif trigger == "can_target_spell":
      return not self.has_status("UNTARGETABLE") or not self.has_status("SPELL_UNTARGETABLE")
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
      return hasattr(self.template, trigger[:-5]) and self.prompt_user_activate()
    elif "cost" in trigger:
      return True
    else:
      return

  def __str__(self):
    if self.type == "monster":
      return f"{self.name} {self.cost} {self.attack}/{self.health}"
    else:
      return f"{self.name} {self.cost}"


