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


class Headless:

  def __init__(self, duel, player_name="Player"):
    with open("../res/cards/fireplacerock.json", "r") as f:
      cards = json.load(f)
      cards = edict(cards)

    self.cards = cards
    self.player_name = player_name

    self.board = Board()


  def target_other_field(self, player="turn"):
    print("Target a card on the opposing field [0-4]")
    idx = int(input())
    return idx


  def flip_coin(self, result, player="turn"):
    print(f"Flipped a coin: {'Heads!' if result == 1 else 'Tails!'}")

  def update_board(self, enemy_board, my_board, hand, graveyard, deck):
    self.board.enemy_board = enemy_board
    self.board.my_board = my_board
    self.board.hand = hand
    self.board.graveyard = graveyard
    self.board.deck = deck

  def main_phase_prompt(self, main_phase_2=False):
    if main_phase_2:
      print("It is Main Phase 2")
    else:
      print("It is Main Phase")
    print(f"Commands: summon, activate_hand, activate_board, pass")
    print(">>> ", end="")
    command = input().split()
    try:
      match command:
        case ("summon", hand_idx, board_idx) | ("s", hand_idx, board_idx):
          return ("summon", int(hand_idx), int(board_idx))
        case ("activate_hand", hand_idx) | ("ah", hand_idx):
          return ("activate_hand", int(hand_idx))
        case ("activate_board", board_idx) | ("ab", board_idx):
          return ("activate_board", int(boar_idx))
        case ("pass"):
          return ("pass")
        case (other, *args):
          raise ValueError(other)
    except ValueError:
      print("Unable to Parse Command")

  def battle_phase_prompt(self):
    print(f"Commands: attack, attack_directly, pass")
    print(">>> ", end="")
    command = input().split()
    try:
      match command:
        case ("attack", attacker_idx, attackee_idx) | ("a", attacker_idx, attackee_idx):
          return ("attack", int(hand_idx), int(board_idx))
        case ("attack_directly", attacker_idx) | ("ad", attacker_idx):
          return ("attack_directly", int(attacker_idx))
        case ("pass"):
          return ("pass")
        case (other, *args):
          raise ValueError(other)
    except ValueError:
      print("Unable to Parse Command")



def test(self):
  deck1 = ["magikarp", "magikarp", "magikarp", "pikachu", "pikachu", "pikachu", "mudkip", "mudkip", "mudkip", "grovyle", "megalopunny", "megalopunny", "megalopunny"]
  deck2 = ["magikarp", "magikarp", "magikarp", "pikachu", "pikachu", "pikachu", "mudkip", "mudkip", "mudkip", "grovyle", "megalopunny", "megalopunny", "megalopunny"]
  deck1 = ["chansey"] * 100
  deck2 = ["wailord"]*100

  deck1 = [self.cards[name] for name in deck1]
  deck1 = [card_api.Template(card) for card in deck1]

  deck2 = [self.cards[name] for name in deck2]
  deck2 = [card_api.Template(card) for card in deck2]

  p1 = Headless(duel, "Player 1")
  p2 = Headless(duel, "Player 2")
  duel = duel_api.Duel(deck1, deck2, p1, p2)
  p1 = Headless("Player 1")
  p2 = Headless("Player 2")

  duel.start_duel()
  duel.start_turn(first=True)
  while True:
    print(f"\nPlayer {duel.cur_turn} turn")
    print(f"Your LP: {duel.turn_p.life} Mana: {duel.turn_p.mana} / {duel.turn_p.mana_max} | Mana: {duel.other_p.mana} / {duel.other_p.mana_max} Other LP: {duel.other_p.life}")
    print("Board: ", duel.other_p.board_str())
    print("     : ", duel.turn_p.board_str())
    print("Hand:  ", duel.turn_p.hand_str())
    print(f"Commands: summon, attack, attack_directly, monster_effect, pass")
    try:
      command = input().split(" ")
      if command[0] == "summon" or command[0] == "s":
        try:
          hand_idx = int(command[1])
          board_idx = int(command[2])
        except:
          raise InvalidSyntax("s [hand_pos] [board_pos]")

        card = duel.play_hand(hand_idx)
        duel.summon(card, board_idx)
      elif command[0] == "attack" or command[0] == "a":
        attacker_idx = int(command[1])
        attackee_idx = int(command[2])
        duel.attack(attacker_idx, attackee_idx)
      elif command[0] == "attack_directly" or command[0] == "ad":
        attacker_idx = int(command[1])
        duel.attack_directly(attacker_idx)
      elif command[0] == "monster_effect" or command[0] == "me":
        board_idx = int(command[1])
        duel.activate_on_board(board_idx)
      elif command[0] == "pass" or command[0] == "p":
        duel.end_turn()
        duel.start_turn()

    except InvalidSyntax as e:
      print(f"Invalid Syntax: {e}")
    except InvalidMove as e:
      print(f"Invalid Move: {e}")
    except GameOver as e:
      print(f"\nGame Over. {e}")
      break


if __name__ == '__main__':
  test()

