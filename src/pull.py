import random
import time

import json
from easydict import EasyDict as edict

with open("../res/cards/fireplacerock.json", "r") as f:
  cards = json.load(f)
  cards = edict(cards)

C = []
R = []
SR = []
UR = []
XR = []
for card in cards.values():
  if card.rarity == "C":
    C.append(card)
  if card.rarity == "R":
    R.append(card)
  if card.rarity == "SR":
    SR.append(card)
  if card.rarity == "UR":
    UR.append(card)
  if card.rarity == "XR":
    XR.append(card)

def gen_card(odds=[0.649, 0.25, 0.075, 0.025, 0.001]):
  num = random.random()
  cumsum = 0
  for odd, base in zip(odds, [C, R, SR, UR, XR]):
    if num <= odd + cumsum:
      return random.choice(base)
    cumsum += odd


def rarity_value(card):
  if card.rarity == "C":
    return 4
  if card.rarity == "R":
    return 3
  if card.rarity == "SR":
    return 2
  if card.rarity == "UR":
    return 1
  if card.rarity == "XR":
    return 0


def pull(n):
  pulls = []

  print("Press enter to pull the next pack (10 packs total)")

  for i in range(n//8):
    input()
    print(f"PACK {i+1}")
    pack = [gen_card() for _ in range(7)]
    if i == n // 8 - 1:
      pack.append(gen_card(odds=[0, 0, 0.899, 0.10, 0.001]))
    else:
      pack.append(gen_card(odds=[0, 0.899, 0.075, 0.025, 0.001]))

    for j, card in enumerate(pack):
      print(f"{card.rarity: <3} ", end="", flush=True)
      if card.rarity == "SR" or card.rarity == "UR":
        time.sleep(0.500)
        print(".", end="", flush=True)
        time.sleep(0.500)
        print(" .", end="", flush=True)
        time.sleep(0.500)
        print(" .", end="", flush=True)
        time.sleep(0.500)
        print("\r", end="")
        print(f"{card.rarity: <3} ", end="")
      elif card.rarity == "C" or card.rarity == "R":
        time.sleep(0.200)
      print(f"{card.name}           ")

    print("")
    pulls += pack

  pulls.sort(key=lambda card: str(rarity_value(card)) + card.name)
  for card in pulls:
    print(f"{card.rarity: <3} {card.name}           ")

  return pulls



if __name__ == '__main__':
  print("What is your name?")
  name = input().strip().lower()
  pulls = pull(80)
  with open(f"../database/{name}.cards", "a") as f:
    for card in pulls:
      f.write(card.uuid + "\n")
