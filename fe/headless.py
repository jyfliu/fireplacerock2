import random
import sys
import os
import threading

import yaml
from easydict import EasyDict as edict

import game_state

class InvalidSyntax(BaseException):
  def __init__(self, message=""):
    self.message = message
  def __str__(self):
    return self.message


class Headless:

  def __init__(self, player_name="Player"):
    self.player_name = player_name

    self.will_end_turn = False
    self.is_other_turn = True

    self.owner = game_state.Player()
    self.oppon = game_state.Player()

    self.print_last = 22
    self.msg_history = [""] * self.print_last

    self.lock = threading.Lock()


  def init_game_state(self, extradeck):
    for card in extradeck:
      self.owner.extradeck.add(card)
    self.owner.extradeck.sort()


  def prompt_user_activate(self, effect_name):
    with self.lock:
      while True:
        print(f"Activate {effect_name}'s effect?' [y/n]")
        x = input().strip().lower()
        if x == "y": return True
        if x == "n": return False

  def prompt_user_select(self, cards):
    return self.prompt_user_select_multiple(cards, amounts=[1])[0]

  def prompt_user_select_multiple(self, cards, amounts):
    if not cards or not amounts:
      return []
    with self.lock:
      if len(amounts) == 1:
        if amounts[0] == 1:
          amount_str = "a card"
        else:
          amount_str = f"{amounts[0]} cards"
      elif amounts == list(range(len(amounts))):
        amount_str = f"up to {amounts[-1]} cards"
      else:
        amount_str = f", ".join([str(amount) for amount in amounts[:-1]])
        amount_str += f", or {amounts[-1]} cards"

      remaining_cards = [c for c in cards]
      selected = []
      print(f"Select {amount_str} [0-{len(remaining_cards) - 1}], -1 to stop selecting")
      done = False
      for _ in range(max(amounts)):
        if done:
          break
        for i, (loc, card) in enumerate(remaining_cards):
          print(f"{i: >2} {loc + ':': <15} {game_state.Card(card)}")
        while True:
          idx = int(input())
          if 0 <= idx < len(remaining_cards):
            selected.append(remaining_cards[idx][1])
            del remaining_cards[idx]
            break
          elif idx == -1:
            done = True
            break
          print(f"Select {amount_str} [0-{len(remaining_cards) - 1}], -1 to stop selecting")
      if len(selected) not in amounts:
        print("Selected an invalid amounts")
        return []
      retval = []
      for i, (_, card) in enumerate(cards):
        if card in selected:
          retval.append(i)
      return retval

  def prompt_user_select_text(self, options):
    if not options:
      return -1
    with self.lock:
      print(f"Select one [0-{len(options) - 1}]")
      for i, opt in enumerate(options):
        # loc in ["hand", "field", "deck", "banished",
        # "oppon_hand", "oppon_field", "oppon_deck", "oppon_banished"]
        print(f"{i: >2} {opt}")
      while True:
        idx = int(input())
        if 0 <= idx < len(options):
          return idx
        print(f"Select one [0-{len(options) - 1}]")

  def prompt_user_select_board(self, nums):
    if not nums:
      return -1
    with self.lock:
      print(f"Select an empty board index: {nums}")
      while True:
        idx = int(input())
        if idx in nums:
          return idx
        print(f"Select an empty board index: {nums}")

  def take_damage(self, amount):
    self.owner.life -= amount

  def oppon_take_damage(self, amount):
    self.oppon.life -= amount

  def pay_mana(self, amount):
    self.owner.mana -= amount

  def oppon_pay_mana(self, amount):
    self.oppon.mana -= amount

  def restore_mana(self, mana, mana_max):
    self.owner.mana = mana
    self.owner.mana_max = mana_max

  def oppon_restore_mana(self, mana, mana_max):
    self.oppon.mana = mana
    self.oppon.mana_max = mana_max

  def flip_coin(self, result):
    self.msg_history.append(f"Flipped a coin: {'Heads!' if result == 1 else 'Tails!'}")

  def display_message(self, msg):
    self.msg_history.append(msg)

  def game_over(self, winner):
    with self.lock:
      if winner == 0:
        print("Game drawn")
      elif winner == 1:
        print("You win!!")
      else:
        print("You lose :(")
      sys.exit()


  def _move_card(self, player, card, from_loc, to_loc, idx):
    match from_loc:
      case "field":
        player.board.delete(card)
      case other:
        if other != "unknown":
          getattr(player, from_loc).remove(card)

    match to_loc:
      case "hand":
        player.hand.add(card).sort()

      case "field":
        player.board[idx] = card

      case "graveyard":
        player.graveyard.append(card)

      case "banished":
        player.banished.append(card)

      case "deck":
        # player can't see into the deck
        pass
      case "extradeck":
        player.extradeck.add(card).sort()
    self.print_board()

  def move_card(self, card, from_loc, to_loc, idx):
    card = game_state.Card(card)
    self._move_card(self.owner, card, from_loc, to_loc, idx)

  def move_oppon_card(self, card, from_loc, to_loc, idx):
    card = game_state.Card(card)
    self._move_card(self.oppon, card, from_loc, to_loc, idx)

  def apply_status(self, uuid, status, duration, expiry):
    for card in self.owner.cards + self.oppon.cards:
      if card.uuid == uuid:
        card.status.append([status, duration, expiry])
    self.print_board()

  def end_turn(self):
    self.is_other_turn = True
    for card in self.owner.cards + self.oppon.cards:
      new_status = []
      for st in card.status:
        if st[1] < 0:
          new_status.append(st)
        elif st[1] == 0:
          pass # expire status (NEED TO CHECK WHAT STGE IT IS!!)
        else:
          st[1] = st[1] - 1
          new_status.append(st)
      card.status = new_status
    self.print_board()

  def card_change_name(self, uuid, new_name):
    for card in self.owner.cards + self.oppon.cards:
      if card.uuid == uuid:
        card.name = new_name

  def card_gain(self, uuid, source, attack, health):
    for card in self.owner.cards + self.oppon.cards:
      if card.uuid == uuid:
        card.attack += attack
        card.health += health
    self.print_board()

  def card_lose(self, uuid, source, attack, health):
    for card in self.owner.cards + self.oppon.cards:
      if card.uuid == uuid:
        card.attack -= attack
        card.health -= health
    self.print_board()

  def card_take_damage(self, uuid, source, amount):
    for card in self.owner.cards + self.oppon.cards:
      if card.uuid == uuid:
        card.health -= amount
    self.print_board()

  def card_set(self, uuid, source, attack, health):
    for card in self.owner.cards + self.oppon.cards:
      if card.uuid == uuid:
        card.attack = attack
        card.health = health
    self.print_board()

  def print_board(self):
    with self.lock:
      print("\033c", end="")
      if self.is_other_turn:
        print("Their turn")
      else:
        print(f"Your turn")
      print(f"Your LP: {self.owner.life} Mana: {self.owner.mana} / {self.owner.mana_max} | Mana: {self.oppon.mana} / {self.oppon.mana_max} Other LP: {self.oppon.life}")
      print("Board: ", self.oppon.board_str())
      print("     : ", self.owner.board_str())
      print("Hand:  ", self.owner.hand_str())
      print()
      print("-" * 20)
      for line in self.msg_history[-self.print_last:]:
        print(line)
      print("-" * 20)
      if self.is_other_turn:
        print("It is the opponent's turn.")

  def print_card(self, card):
    self.msg_history.append("")
    self.msg_history.append(card)
    if not card.status:
      self.msg_history.append("Status: None")
    else:
      for st, dur, _ in card.status:
        self.msg_history.append(f"Status: {st.lower()} for {dur} more turns")
    if card.description:
      self.msg_history.append("")
      self.msg_history.append(card.description)
    if card.flavour:
      self.msg_history.append("")
      self.msg_history.append(card.flavour)

  def draw_phase_prompt(self):
    # YOU DREW X
    self.is_other_turn = False
    self.will_end_turn = False
    return ["pass"]

  def main_phase_prompt(self, main_phase_2=False):
    if self.will_end_turn:
      return ["pass"]
    self.print_board()
    with self.lock:
      if main_phase_2:
        print("It is Main Phase 2")
      else:
        print("It is Main Phase")
      print(f"Commands: info, summon, summon_extradeck, activate_spell, activate_board, pass, end")
      print(">>> ", end="")
    command = input().split()
    try:
      hand = [("hand", card) for card in self.owner.hand]
      field = [("field", card) for card in self.owner.field]
      oppon_field = [("oppon_field", card) for card in self.oppon.field]
      extradeck = [("extradeck", card) for card in self.owner.extradeck]

      empty_board = [i for i in range(5) if self.owner.board[i] is None]
      filled_board = [i for i in range(5) if self.owner.board[i] is not None]

      match command:
        case ["info"] | ["i"]:
          cards = hand + field + oppon_field
          _, card = cards[self.prompt_user_select(cards)]
          self.print_card(card)
        case ["info", idx] | ["i", idx]:
          try:
            cards = self.owner.hand + self.owner.field + self.oppon.field
            self.print_card(cards[int(idx)])
          except:
            raise ValueError()

        case ["summon"] | ["s"]:
          hand_idx = self.prompt_user_select(hand)
          board_idx = self.prompt_user_select_board(empty_board)
          return ["summon", hand_idx, board_idx]
        case ["summon", hand_idx, board_idx] | ["s", hand_idx, board_idx]:
          return ["summon", int(hand_idx), int(board_idx)]

        case ["summon_extradeck"] | ["se"]:
          ed_idx = self.prompt_user_select(extradeck)
          board_idx = self.prompt_user_select_board(empty_board)
          return ["summon_extradeck", ed_idx, board_idx]
        case ["summon_extradeck", ed_idx, board_idx] | ["se", ed_idx, board_idx]:
          return ["summon_extradeck", int(ed_idx), int(board_idx)]

        case ["activate_spell"] | ["as"]:
          hand_idx = self.prompt_user_select(hand)
          return ["activate_spell", hand_idx]
        case ["activate_spell", hand_idx] | ["as", hand_idx]:
          return ["activate_spell", int(hand_idx)]

        case ["activate_board"] | ["ab"]:
          board_idx = self.prompt_user_select(field)
          board_idx = filled_board[board_idx]

          return ["activate_board", board_idx]
        case ["activate_board", board_idx] | ["ab", board_idx]:
          return ["activate_board", int(board_idx)]
        case ["pass"] | ["p"]:
          return ["pass"]
        case ["end"] | ["e"]:
          self.will_end_turn = True
          return ["pass"]
        case [other, *_]:
          raise ValueError(other)
        case _:
          raise ValueError
    except ValueError:
      self.msg_history.append("Unable to Parse Command")

  def battle_phase_prompt(self):
    if self.will_end_turn:
      return ["pass"]
    self.print_board()
    with self.lock:
      print("It is Battle Phase")
      print(f"Commands: attack, attack_directly, pass, end")
      print(">>> ", end="")
    command = input().split()
    try:
      hand = [("hand", card) for card in self.owner.hand]
      field = [("field", card) for card in self.owner.field]
      oppon_field = [("oppon_field", card) for card in self.oppon.field]

      empty_board = [i for i in range(5) if self.owner.board[i] is None]
      filled_board = [i for i in range(5) if self.owner.board[i] is not None]

      match command:
        case ["attack", attacker_idx, attackee_idx] | ["a", attacker_idx, attackee_idx]:
          return ["attack", int(attacker_idx), int(attackee_idx)]
        case ["attack"] | ["a"]:
          if field and oppon_field:
            attacker_idx = self.prompt_user_select(field)
            attackee_idx = self.prompt_user_select(oppon_field)
          else:
            raise ValueError()
          return ["attack", attacker_idx, attackee_idx]

        case ["attack_directly", attacker_idx] | ["ad", attacker_idx]:
          return ["attack_directly", int(attacker_idx)]
        case ["attack_directly"] | ["ad"]:
          attacker_idx = self.prompt_user_select(field)
          attacker_idx = filled_board[attacker_idx]
          return ["attack_directly", attacker_idx]

        case ["pass"] | ["p"]:
          return ["pass"]
        case ["end"] | ["e"]:
          self.will_end_turn = True
          return ["pass"]
        case [other, _] | [other]:
          raise ValueError(other)
    except ValueError:
      self.msg_history.append("Unable to Parse Command")

