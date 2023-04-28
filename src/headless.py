import json
import card_api
import duel_api
import io

from easydict import EasyDict as edict
from callbacks import *

class InvalidSyntax(BaseException):
  def __init__(self, message=""):
    self.message = message
  def __str__(self):
    return self.message


class Board:
  def __init__(self):
    self.enemy_board = [None] * 5
    self.my_board = [None] * 5
    self.hand = []
    self.graveyard = []
    self.deck = []
    self.my_lp = 3000
    self.enemy_lp = 3000
    self.my_mana = 0
    self.my_mana_max = 0
    self.enemy_mana = 0
    self.enemy_mana_max = 0


class Headless:

  def __init__(self, player_name="Player"):
    self.player_name = player_name

    self.board = Board()

    self.end_turn = False

  def prompt_user_activate(self, effect_name):
    print(f"Activate {effect_name}'s effect?' [y/n]")
    x = input().strip().lower()
    return x == "y"


  def target_self_board_empty(self):
    raise

  def target_other_board_empty(self):
    raise

    # target card on the field
    # optionally accepts a lambda to filter
    # returns card of monster
  def target_field(self):
    raise

  def target_self_field(self):
    pass

  def target_other_field(self, filter=lambda x: True):
    print("Target a card on the opposing field [0-4]")
    idx = int(input())
    return idx

    # select monster on the field
    # optionally accepts a lambda to filter
    # returns monster
  def select_field(self):
    raise

  def select_self_field(self):
    raise

  def select_other_field(self):
    raise


    # select card from deck
    # optionally accepts a lambda to filter
    # returns card
  def select_self_deck(self):
    raise

    # select_other_deck = self.io.select_other_deck

    # select card from deck
    # optionally accepts a lambda to filter
    # returns card
  def select_self_graveyard(self):
    raise

  def select_other_graveyard(self):
    raise


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

  def print_board(self):
    print(f"\n{self.player_name}'s turn")
    print(f"Your LP: {self.duel.turn_p.life} Mana: {self.duel.turn_p.mana} / {self.duel.turn_p.mana_max} | Mana: {self.duel.other_p.mana} / {self.duel.other_p.mana_max} Other LP: {self.duel.other_p.life}")
    print("Board: ", self.duel.other_p.board_str())
    print("     : ", self.duel.turn_p.board_str())
    print("Hand:  ", self.duel.turn_p.hand_str())

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
    print(f"Commands: summon, activate_hand, activate_board, pass, end")
    print(">>> ", end="")
    command = input().split()
    try:
      match command:
        case ["summon", hand_idx, board_idx] | ["s", hand_idx, board_idx]:
          return ["summon", int(hand_idx), int(board_idx)]
        case ["activate_hand", hand_idx] | ["ah", hand_idx]:
          return ["activate_hand", int(hand_idx)]
        case ["activate_board", board_idx] | ["ab", board_idx]:
          return ["activate_board", int(boar_idx)]
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
  with open("../res/cards/fireplacerock.json", "r") as f:
    cards = json.load(f)
    cards = edict(cards)

  deck1 = ["magikarp", "magikarp", "magikarp", "pikachu", "pikachu", "pikachu", "mudkip", "mudkip", "mudkip", "grovyle", "megalopunny", "megalopunny", "megalopunny"]
  deck2 = ["magikarp", "magikarp", "magikarp", "pikachu", "pikachu", "pikachu", "mudkip", "mudkip", "mudkip", "grovyle", "megalopunny", "megalopunny", "megalopunny"]
  deck1 = ["jirachi"] * 100
  deck2 = ["hooh"]*100

  deck1 = [cards[name] for name in deck1]
  deck1 = [card_api.Template(card) for card in deck1]

  deck2 = [cards[name] for name in deck2]
  deck2 = [card_api.Template(card) for card in deck2]

  p1 = Headless("Player 1")
  p2 = Headless("Player 2")
  duel = duel_api.Duel(deck1, deck2, p1, p2)
  duel.p1.mana_max = 10
  duel.p2.mana_max = 10
  # TMP STUFF for printing board
  p1.duel = duel
  p2.duel = duel

  duel.start_duel()


if __name__ == '__main__':
  test()

