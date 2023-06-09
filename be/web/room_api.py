import socketio
import yaml
from easydict import EasyDict as edict

import gameplay.callbacks
import gameplay.duel_api as duel_api
import gameplay.card_api as card_api
from . import server as se

def serialize_card(card):
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

  dict["description"] = card.template.description
  dict["flavour"] = card.template.flavour

  return dict

# TODO HANDLE timeouts
class PlayerIO:

  def __init__(self, name):
    self.name = name

  @property
  def sid(self):
    return se.state.name_to_sid[self.name]

  def init_game_state(self, extradeck):
    extradeck = [serialize_card(card) for card in extradeck]
    se.sio.emit("init_game_state", extradeck, room=self.sid)

  def prompt_user_activate(self, effect_name):
    response = se.sio.call("prompt_user_activate", effect_name, sid=self.sid, timeout=9999)

    assert response in [True, False]
    return response

  def prompt_user_select(self, cards, amount=1):
    if amount == -1:
      amount = list(range(len(cards) + 1))
    elif not isinstance(amount, list):
      amount = [amount]
    cards = [(loc, serialize_card(card)) for loc, card in cards]
    response = se.sio.call("prompt_user_select_cards", (cards, amount), sid=self.sid, timeout=9999)

    if len(response) == 1:
      assert response[0] in range(len(cards))
      return response[0]
    else:
      return response

  def prompt_user_select_text(self, options):
    response = se.sio.call("prompt_user_select_text", options, sid=self.sid, timeout=9999)

    assert response in range(len(options))
    return response

  def prompt_user_select_board(self, nums):
    response = se.sio.call("prompt_user_select_board", nums, sid=self.sid, timeout=9999)

    assert response in nums
    return response

  def take_damage(self, amount):
    se.sio.emit("take_damage", amount, room=self.sid)

  def oppon_take_damage(self, amount):
    se.sio.emit("oppon_take_damage", amount, room=self.sid)

  def pay_mana(self, amount):
    se.sio.emit("pay_mana", amount, room=self.sid)

  def oppon_pay_mana(self, amount):
    se.sio.emit("oppon_pay_mana", amount, room=self.sid)

  def restore_mana(self, mana, mana_max):
    se.sio.emit("restore_mana", (mana, mana_max), room=self.sid)

  def oppon_restore_mana(self, mana, mana_max):
    se.sio.emit("oppon_restore_mana", (mana, mana_max), room=self.sid)

  def flip_coin(self, result):
    se.sio.emit("flip_coin", result, room=self.sid)

  def display_message(self, msg):
    se.sio.emit("display_message", msg, room=self.sid)

  def game_over(self, winner):
    se.sio.emit("game_over", winner, room=self.sid)

  def move_card(self, card, from_loc, to_loc, idx):
    se.sio.emit("move_card", (serialize_card(card), from_loc, to_loc, idx), room=self.sid)

  def move_oppon_card(self, card, from_loc, to_loc, idx):
    se.sio.emit("move_oppon_card", (serialize_card(card), from_loc, to_loc, idx), room=self.sid)

  def apply_status(self, uuid, status, duration, expiry):
    se.sio.emit("apply_status", (uuid, status, duration, expiry), room=self.sid)

  def end_turn(self):
    se.sio.emit("end_turn", room=self.sid)

  def card_change_name(self, uuid, new_name):
    se.sio.emit("card_change_name", (uuid, new_name), room=self.sid)

  # TODO do source
  def card_gain(self, uuid, source, attack, health):
    se.sio.emit("card_gain", (uuid, None, attack, health), room=self.sid)

  def card_lose(self, uuid, source, attack, health):
    se.sio.emit("card_lose", (uuid, None, attack, health), room=self.sid)

  def card_take_damage(self, uuid, source, amount):
    se.sio.emit("card_take_damage", (uuid, None, amount), room=self.sid)

  def card_set(self, uuid, source, attack, health):
    se.sio.emit("card_set", (uuid, None, attack, health), room=self.sid)

  def draw_phase_prompt(self):
    response = se.sio.call("draw_phase_prompt", sid=self.sid, timeout=9999)
    return response

  def main_phase_prompt(self, main_phase_2=False):
    response = se.sio.call("main_phase_prompt", main_phase_2, sid=self.sid, timeout=9999)
    return response

  def battle_phase_prompt(self):
    response = se.sio.call("battle_phase_prompt", sid=self.sid, timeout=9999)
    return response


class Room:

  def __init__(self, config, p1_name, p2_name):
    self.config = config
    self.p1_name = p1_name
    self.p2_name = p2_name

  def start_duel(self, deck1, deck2):
    p1 = PlayerIO(self.p1_name)
    p2 = PlayerIO(self.p2_name)

    with open("../res/cards/fireplacerock.yaml", "r") as f:
      cards = yaml.safe_load(f)
      cards = edict(cards)

    sd1, ed1 = deck1
    sd1 = [cards[name] for name in sd1]
    sd1 = [card_api.Template(card) for card in sd1]

    ed1 = [cards[name] for name in ed1]
    ed1 = [card_api.Template(card) for card in ed1]

    sd2, ed2 = deck2
    sd2 = [cards[name] for name in sd2]
    sd2 = [card_api.Template(card) for card in sd2]

    ed2 = [cards[name] for name in ed2]
    ed2 = [card_api.Template(card) for card in ed2]

    card_templates = {
        uuid: card_api.Template(card) for uuid, card in cards.items()
    }
    duel = duel_api.Duel(card_templates, (sd1, ed1), (sd2, ed2), p1, p2)

    duel.start_duel()


