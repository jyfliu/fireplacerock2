import multiprocessing as mp
import socketio
import yaml
from easydict import EasyDict as edict

import gameplay.callbacks
import gameplay.duel_api as duel_api
import gameplay.card_api as card_api
from . import server as se

# TODO HANDLE timeouts
class PlayerIO:

  def __init__(self, name):
    self.name = name
    self.duel = None
    self.player_obj = None
    self.sprite_cache = set()

  def connect(self, duel, player_obj):
    self.duel = duel
    self.player_obj = player_obj

  def serialize_card(self, card):
    if card is None:
      return None
    duel = self.duel
    player = self.player_obj
    dict = {}
    dict["name"] = card.name
    dict["cost"] = card.cost
    dict["type"] = card.type
    if card.type == "monster":
      dict["attack"] = card.attack
      dict["health"] = card.health
      dict["original_attack"] = card.original_attack
      dict["original_health"] = card.original_health
    dict["uuid"] = card.uuid
    dict["template_id"] = card.id

    dict["can_activate"] = card.can("activate")
    dict["can_activate_hand"] = card.can("activate_hand")
    dict["can_attack"] = card.can("attack")
    dict["can_attack_directly"] = card.can("attack_directly")
    dict["can_summon"] = card.can("summon")
    dict["can_summon_extradeck"] = card.can("summon_extradeck")

    dict["description"] = card.template.description
    dict["flavour"] = card.template.flavour

    if card.uuid not in self.sprite_cache and card.template.sprite:
      dict["sprite"] = card.template.sprite
    if card.uuid not in self.sprite_cache and card.template.mini_sprite:
      dict["mini_sprite"] = card.template.mini_sprite
    dict["bkgd_colour"] = card.template.bkgd_colour

    return dict

  @property
  def sid(self):
    return se.state.name_to_sid[self.name]

  def init_game_state(self, owner_player, oppon_player):
    def serialize_player(player):
      return {
        "life": player.life,
        "mana": player.mana,
        "mana_max": player.mana_max,
        "status": player.status,
      }
    owner_hand = [self.serialize_card(card) for card in owner_player.hand]
    owner_monsters = [self.serialize_card(card) for card in owner_player.board]
    owner_graveyard = [self.serialize_card(card) for card in owner_player.graveyard]
    owner_banished = [self.serialize_card(card) for card in owner_player.banished]
    owner_maindeck = len(owner_player.deck)
    owner_extradeck = [self.serialize_card(card) for card in owner_player.extradeck]
    oppon_hand = len(oppon_player.hand)
    oppon_monsters = [self.serialize_card(card) for card in oppon_player.board]
    oppon_graveyard = [self.serialize_card(card) for card in oppon_player.graveyard]
    oppon_banished = [self.serialize_card(card) for card in oppon_player.banished]
    oppon_maindeck = len(oppon_player.deck)
    oppon_extradeck = len(oppon_player.extradeck)
    se.emit(
      "init_game_state",
      (
        serialize_player(owner_player),
        serialize_player(oppon_player),
        owner_hand,
        owner_monsters,
        owner_graveyard,
        owner_banished,
        owner_maindeck,
        owner_extradeck,
        oppon_hand,
        oppon_monsters,
        oppon_graveyard,
        oppon_banished,
        oppon_maindeck,
        oppon_extradeck,
      ),
      sid=self.sid,
    )

  def prompt_user_activate(self, effect_name):
    response = se.call("prompt_user_activate", effect_name, sid=self.sid)

    assert response in [True, False]
    return response

  def prompt_user_select(self, cards, amount=1):
    if amount == -1:
      amount = list(range(len(cards) + 1))
    elif not isinstance(amount, list):
      amount = [amount]
    else:
      amount = list(sorted(amount))
    cards = [(loc, self.serialize_card(card)) for loc, card in cards]
    response = se.call("prompt_user_select_cards", (cards, amount), sid=self.sid)
    response = [int(i) for i in response]

    return response

  def prompt_user_select_text(self, options):
    response = se.call("prompt_user_select_text", options, sid=self.sid)
    response = int(response)

    assert response in range(len(options))
    return response

  def prompt_user_select_board(self, nums):
    response = se.call("prompt_user_select_board", nums, sid=self.sid)
    response = int(response)

    assert response in nums
    return response

  def take_damage(self, amount):
    se.emit("take_damage", amount, sid=self.sid)

  def oppon_take_damage(self, amount):
    se.emit("oppon_take_damage", amount, sid=self.sid)

  def pay_mana(self, amount):
    se.emit("pay_mana", amount, sid=self.sid)

  def oppon_pay_mana(self, amount):
    se.emit("oppon_pay_mana", amount, sid=self.sid)

  def restore_mana(self, mana, mana_max):
    se.emit("restore_mana", (mana, mana_max), sid=self.sid)

  def oppon_restore_mana(self, mana, mana_max):
    se.emit("oppon_restore_mana", (mana, mana_max), sid=self.sid)

  def flip_coin(self, result):
    se.emit("flip_coin", result, sid=self.sid)

  def display_message(self, msg):
    se.emit("display_message", msg, sid=self.sid)

  def game_start(self):
    se.emit("game_start", sid=self.sid)

  def game_over(self, winner):
    se.state.record_game_result(self.name, winner)
    se.emit("game_over", winner, sid=self.sid)

  def move_card(self, card, from_loc, to_loc, idx):
    se.emit("move_card", (self.serialize_card(card), from_loc, to_loc, idx), sid=self.sid)

  def move_oppon_card(self, card, from_loc, to_loc, idx):
    se.emit("move_oppon_card", (self.serialize_card(card), from_loc, to_loc, idx), sid=self.sid)

  def apply_status(self, uuid, status, duration, expiry):
    se.emit("apply_status", (uuid, status, duration, expiry), sid=self.sid)

  def clear_status(self, uuid, status):
    se.emit("clear_status", (uuid, status), sid=self.sid)

  def end_turn(self):
    se.emit("end_turn", sid=self.sid)

  def card_change_name(self, uuid, new_name):
    se.emit("card_change_name", (uuid, new_name), sid=self.sid)

  # TODO do source
  def card_gain(self, uuid, source, attack, health):
    se.emit("card_gain", (uuid, None, attack, health), sid=self.sid)

  def card_lose(self, uuid, source, attack, health):
    se.emit("card_lose", (uuid, None, attack, health), sid=self.sid)

  def card_take_damage(self, uuid, source, amount):
    se.emit("card_take_damage", (uuid, None, amount), sid=self.sid)

  def card_set(self, uuid, source, attack, health):
    se.emit("card_set", (uuid, None, attack, health), sid=self.sid)

  def begin_phase(self, player, phase):
    se.emit("begin_phase", (player, phase), sid=self.sid)

  def wait_input(self, spell_speed):
    se.emit("wait_input", spell_speed, sid=self.sid)


class Room:

  def __init__(self, config, p1_name, p2_name):
    self.config = config
    self.p1_name = p1_name
    self.p2_name = p2_name

  def start_duel(self, deck1, deck2):
    p1 = PlayerIO(self.p1_name)
    p2 = PlayerIO(self.p2_name)

    with open("../res/cards/fireplacerock.yaml", "r", encoding="utf8") as f:
      cards = yaml.safe_load(f)
      cards = edict(cards)

    with mp.Pool(16) as p:
      sd1, ed1 = deck1
      sd1 = [cards[name] for name in sd1]
      sd1 = p.map(card_api.Template, sd1)

      ed1 = [cards[name] for name in ed1]
      ed1 = p.map(card_api.Template, ed1)

      sd2, ed2 = deck2
      sd2 = [cards[name] for name in sd2]
      sd2 = p.map(card_api.Template, sd2)

      ed2 = [cards[name] for name in ed2]
      ed2 = p.map(card_api.Template, ed2)

    card_templates = {
        uuid: card_api.Template(card) for uuid, card in cards.items()
    }
    self.duel = duel_api.Duel(card_templates, (sd1, ed1), (sd2, ed2), p1, p2)

    self.duel.start_duel()

  def player_action(self, player, action):
    if player == self.p1_name:
      self.duel.player_action(1, action)
    elif player == self.p2_name:
      self.duel.player_action(2, action)
    else:
      self.p1.display_message(f"Internal Error 528: unknown player name? {player}")
      self.p2.display_message(f"Internal Error 528: unknown player name? {player}")

  def card_can(self, card_id, action):
    card = self.duel.get_card(card_id)
    return card.can(action)

