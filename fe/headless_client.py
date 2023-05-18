import socketio
from easydict import EasyDict as edict

import headless

player_name = input("Enter your name:\n")
other = input("Enter name of who you want to challenge: [tmp]\n")

sio = socketio.Client()
io = headless.Headless(player_name)

@sio.event
def connect():
  print('Connection established with server')
  sio.emit("login", player_name)
  sio.emit("challenge", other)
  print("waiting")


@sio.event
def disconnect():
  print('Disconnected from server')

@sio.event
def prompt_user_activate(effect_name):
  return io.prompt_user_activate(effect_name)

@sio.event
def prompt_user_select(cards):
  cards = [(loc, edict(card)) for loc, card in cards]
  return io.prompt_user_select(cards)

@sio.event
def prompt_user_select_board(nums):
  return io.prompt_user_select_board(nums)

@sio.event
def take_damage(amount):
  return io.take_damage(amount)

@sio.event
def oppon_take_damage(amount):
  return io.oppon_take_damage(amount)

@sio.event
def pay_mana(amount):
  return io.pay_mana(amount)

@sio.event
def oppon_pay_mana(amount):
  return io.oppon_pay_mana(amount)

@sio.event
def restore_mana(mana, mana_max):
  return io.restore_mana(mana, mana_max)

@sio.event
def oppon_restore_mana(mana, mana_max):
  return io.oppon_restore_mana(mana, mana_max)

@sio.event
def flip_coin(result):
  return io.flip_coin(result)

@sio.event
def display_message(result):
  return io.display_message(result)

@sio.event
def game_over(winner):
  return io.game_over(winner)

@sio.event
def move_card(card, from_loc, to_loc, idx):
  return io.move_card(edict(card), from_loc, to_loc, idx)

@sio.event
def move_oppon_card(card, from_loc, to_loc, idx):
  return io.move_oppon_card(edict(card), from_loc, to_loc, idx)

@sio.event
def apply_status(uuid, status, duration, expiry):
  return io.apply_status(uuid, status, duration, expiry)

@sio.event
def end_turn():
  return io.end_turn()

@sio.event
def card_change_name(uuid, new_name):
  return io.card_change_name(uuid, new_name)

@sio.event
def card_gain(uuid, source, attack, health):
  return io.card_gain(uuid, source, attack, health)

@sio.event
def card_lose(uuid, source, attack, health):
  return io.card_lose(uuid, source, attack, health)

@sio.event
def card_take_damage(uuid, source, amount):
  return io.card_take_damage(uuid, source, amount)

@sio.event
def card_set(uuid, source, attack, health):
  return io.card_set(uuid, source, attack, health)

@sio.event
def draw_phase_prompt():
  return io.draw_phase_prompt()

@sio.event
def main_phase_prompt(main_phase_2=False):
  return io.main_phase_prompt(main_phase_2=False)

@sio.event
def battle_phase_prompt():
  return io.battle_phase_prompt()


sio.connect('http://localhost:9069')
sio.wait()

