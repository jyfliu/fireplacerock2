import json
import card_api
import duel_api
import io

from easydict import EasyDict as edict

class Headless:

  def __init__(self):
    with open("../res/cards/pokemon.json", "r") as f:
      cards = json.load(f)
      cards = edict(cards)

    self.cards = cards


  def target_other_field(self, player="turn"):
    print("Target a card on the opposing field [0-4]")
    idx = int(input())
    return idx


  def run(self):
    deck1 = ["magikarp", "magikarp", "magikarp", "pikachu", "pikachu", "pikachu", "mudkip", "mudkip", "mudkip", "grovyle", "megalopunny", "megalopunny", "megalopunny"]
    deck2 = ["magikarp", "magikarp", "magikarp", "pikachu", "pikachu", "pikachu", "mudkip", "mudkip", "mudkip", "grovyle", "megalopunny", "megalopunny", "megalopunny"]

    deck1 = [self.cards[name] for name in deck1]
    deck1 = [card_api.Template(card) for card in deck1]

    deck2 = [self.cards[name] for name in deck2]
    deck2 = [card_api.Template(card) for card in deck2]

    duel = duel_api.Duel(deck1, deck2, self)
    self.duel = duel
    duel.start_duel()
    duel.start_turn(first=True)
    while True:
      print(f"\nPlayer {duel.cur_turn} turn")
      print(f"Your LP: {duel.turn_p.life} Mana: {duel.turn_p.mana} / {duel.turn_p.mana_max} | Mana: {duel.other_p.mana} / {duel.other_p.mana_max} Other LP: {duel.other_p.life}")
      print("Board: ", duel.other_p.board_str())
      print("     : ", duel.turn_p.board_str())
      print("Hand:  ", duel.turn_p.hand_str())
      print(f"Commands: summon, attack, attack_directly, pass")
      try:
        command = input().split(" ")
        if command[0] == "summon" or command[0] == "s":
          hand_idx = int(command[1])
          board_idx = int(command[2])

          card = duel.play_hand(hand_idx)
          duel.summon(card, board_idx)
        elif command[0] == "attack" or command[0] == "a":
          attacker_idx = int(command[1])
          attackee_idx = int(command[2])
          duel.attack(attacker_idx, attackee_idx)
        elif command[0] == "attack_directly" or command[0] == "ad":
          attacker_idx = int(command[1])
          duel.attack_directly(attacker_idx)
        elif command[0] == "pass" or command[0] == "p":
          duel.end_turn()
          duel.start_turn()

      except duel_api.InvalidMove as e:
        print(f"Invalid Move {e}")
      except duel_api.GameOver as e:
        print(f"\nGame Over. {e}")
        break


if __name__ == '__main__':
  Headless().run()
