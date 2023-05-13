import random
import sys
import os

import yaml
from easydict import EasyDict as edict

import game_state

sys.path.append(os.path.abspath("../be"))

import card_api
import duel_api
import io

from callbacks import *

class InvalidSyntax(BaseException):
  def __init__(self, message=""):
    self.message = message
  def __str__(self):
    return self.message


class Headless:

  def __init__(self, player_name="Player"):
    self.player_name = player_name

    self.end_turn = False

  def init(self, owner, oppon):
    self.owner = game_state.Player(owner)
    self.oppon = game_state.Player(oppon)

  def prompt_user_activate(self, effect_name):
    print(f"Activate {effect_name}'s effect?' [y/n]")
    x = input().strip().lower()
    return x == "y"


  def prompt_user_select(self, cards):
    print(f"Select a card [0-{len(cards) - 1}]")
    for i, (loc, card) in enumerate(cards):
      # loc in ["hand", "field", "deck", "banished",
      # "oppon_hand", "oppon_field", "oppon_deck", "oppon_banished"]
      print(f"{i: >2} {loc + ':': <15} {card}")
    while True:
      idx = int(input())
      if 0 <= idx < len(cards):
        return idx
      print(f"Select a card [0-{len(cards) - 1}]")

  def prompt_user_select_board(self, nums):
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
    print(f"Flipped a coin: {'Heads!' if result == 1 else 'Tails!'}")

  def display_message(self, msg):
    print(msg)

  def game_over(self, winner):
    if winner == 0:
      print("Game drawn")
    elif winner == 1:
      print("You win!!")
    else:
      print("You lose :(")


  def _move_card(self, player, card, from_loc, to_loc, idx):
    match from_loc:
      case "field":
        player.board.delete(card)
      case other:
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

  def move_card(self, card, from_loc, to_loc, idx):
    card = game_state.Card(card)
    self._move_card(self.owner, card, from_loc, to_loc, idx)

  def move_oppon_card(self, card, from_loc, to_loc, idx):
    card = game_state.Card(card)
    self._move_card(self.oppon, card, from_loc, to_loc, idx)

  def print_board(self):
    print(f"\n{self.player_name}'s turn")
    print(f"Your LP: {self.owner.life} Mana: {self.owner.mana} / {self.owner.mana_max} | Mana: {self.oppon.mana} / {self.oppon.mana_max} Other LP: {self.oppon.life}")
    print("Board: ", self.oppon.board_str())
    print("     : ", self.owner.board_str())
    print("Hand:  ", self.owner.hand_str())

  def print_card(self, card):
    print()
    print(card)
    print("Status: ", card.status)
    print()
    print(card.template.description)
    if card.template.flavour:
      print()
      print(card.template.flavour)

  def draw_phase_prompt(self):
    # YOU DREW X
    self.end_turn = False
    pass

  def main_phase_prompt(self, main_phase_2=False):
    if self.end_turn:
      return ["pass"]
    self.print_board()
    if main_phase_2:
      print("It is Main Phase 2")
    else:
      print("It is Main Phase")
    print(f"Commands: info, summon, activate_hand, activate_board, pass, end")
    print(">>> ", end="")
    command = input().split()
    try:
      hand = [("hand", card) for card in self.owner.hand]
      field = [("field", card) for card in self.owner.field]
      oppon_field = [("oppon_field", card) for card in self.oppon.field]

      empty_board = [i for i in range(5) if self.owner.board[i] is None]
      filled_board = [i for i in range(5) if self.owner.board[i] is not None]

      match command:
        case ["info"] | ["i"]:
          cards = hand + field + oppon_field
          _, card = cards[self.prompt_user_select(cards)]
          self.print_card(card)
        case ["info", idx] | ["i", idx]:
          cards = self.owner.hand + self.owner.field + self.oppon.field
          self.print_card(cards[idx])

        case ["summon"] | ["s"]:
          hand_idx = self.prompt_user_select(hand)
          board_idx = self.prompt_user_select_board(empty_board)
          return ["summon", hand_idx, board_idx]
        case ["summon", hand_idx, board_idx] | ["s", hand_idx, board_idx]:
          return ["summon", int(hand_idx), int(board_idx)]

        case ["activate_hand"] | ["ah"]:
          hand_idx = self.prompt_user_select(hand)
          return ["activate_hand", hand_idx]
        case ["activate_hand", hand_idx] | ["ah", hand_idx]:
          return ["activate_hand", int(hand_idx)]

        case ["activate_board"] | ["ab"]:
          board_idx = self.prompt_user_select(field)
          board_idx = filled_board[board_idx]

          return ["activate_board", board_idx]
        case ["activate_board", board_idx] | ["ab", board_idx]:
          return ["activate_board", int(board_idx)]
        case ["pass"] | ["p"]:
          return ["pass"]
        case ["end"] | ["e"]:
          self.end_turn = True
          return ["pass"]
        case [other, *_]:
          raise ValueError(other)
        case _:
          raise ValueError
    except ValueError:
      print("Unable to Parse Command")

  def battle_phase_prompt(self):
    if self.end_turn:
      return ["pass"]
    self.print_board()
    print("It is Battle Phase")
    print(f"Commands: attack, attack_directly, pass, end")
    print(">>> ", end="")
    command = input().split()
    try:
      match command:
        case ["attack", attacker_idx, attackee_idx] | ["a", attacker_idx, attackee_idx]:
          return ["attack", int(attacker_idx), int(attackee_idx)]
        case ["attack_directly", attacker_idx] | ["ad", attacker_idx]:
          return ["attack_directly", int(attacker_idx)]
        case ["pass"] | ["p"]:
          return ["pass"]
        case ["end"] | ["e"]:
          self.end_turn = True
          return ["pass"]
        case [other, _] | [other]:
          raise ValueError(other)
    except ValueError:
      print("Unable to Parse Command")



def test():
  with open("../res/cards/fireplacerock.yaml", "r") as f:
    cards = yaml.safe_load(f)
    cards = edict(cards)

  names = [ # all working cards
    "mew", "unown",
    # "sprightelf",
    "magikarp", "mudkip", "pikachu", "grovyle", "ampharos",
    "blastoise", "wailord", "snorlax", "garchomp", "jirachi", "hooh",
    # "kyogre", "groudon", "giratina",
    "arceus", "gallade", "heracross", "shuckle", "breloom", "chansey",
    "tyranitar", "gengar", "dragonite",
    # "gyarados"
    "salamence", "lugia", "lapras", "turtwig",
    "sprightjet", "sprightblue", "sprightpixie", "windupkitten",
    "livetwinlilla", "livetwinkisikil", "livetwintroublesunny", "omen",
    # "brimstone", "viper",
    "reyna",
    # "cypher", "neon",
    "jett", "phoenix", "dartmonkey",
    # "supermonkey", "johnnywyles", "riverwyles", "redamogus", "zoe"
    "lopunny", "megalopunny",
  ]

  #deck1 = ["livetwinlilla", "livetwinkisikil", "livetwintroublesunny"] * 16
  #deck2 = ["sprightblue", "mew", "arceus"] * 16
  deck1 = random.sample(names, k=16) * 3
  deck2 = random.sample(names, k=16) * 3

  deck1 = [cards[name] for name in deck1]
  deck1 = [card_api.Template(card) for card in deck1]

  deck2 = [cards[name] for name in deck2]
  deck2 = [card_api.Template(card) for card in deck2]

  p1 = Headless("Player 1")
  p2 = Headless("Player 2")
  duel = duel_api.Duel(deck1, deck2, p1, p2)
  duel.p1.mana_max = 10
  duel.p2.mana_max = 10

  p1.init(duel.p1, duel.p2)
  p2.init(duel.p2, duel.p1)

  duel.start_duel()


if __name__ == '__main__':
  test()

