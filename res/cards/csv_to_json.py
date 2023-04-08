import sys
import pandas as pd
import json

functions = [
  "on_summon",
  "on_destroyed",
  "on_destroy_battle",
  "on_destroyed_battle",
  "on_send_graveyard",
  "on_activate",
  "on_attack",
  "on_attack_directly",
  "on_attacked",
  "on_take_damage",
  "on_take_battle_damage",
  "end_attack",
  "end_attacked",
]

def int_or_nothing(str):
  try:
    return int(str)
  except ValueError:
    return -1


csv_path = sys.argv[1]
assert csv_path[-4:] == ".csv"

df = pd.read_csv(csv_path)
df.fillna(value="", inplace=True)

cards = {}
print(df)

for _, row in df.iterrows():
  if not row["Set"]:
    continue
  card = {}
  card["name"] = row["Name"]
  card["type"] = row["Type"]
  card["cost"] = int_or_nothing(row["Cost"])
  if card["type"] == "Monster":
    card["attack"] = int_or_nothing(row["Attack"])
    card["health"] = int_or_nothing(row["Health"])
  if row["Flavour"]:
    card["flavour"] = row["Flavour"]
  if row["Description"]:
    card["description"] = row["Description"]
  else:
    card["description"] = ""
  card["id"] = int_or_nothing(row["ID"])
  card["rarity"] = row["Rarity"]

  for fn in functions:
    card[fn] = row[fn].replace('\\n', '\n')

  id = row["Name"].lower()
  id = ''.join(ch for ch in id if ch.isalnum())
  card["uuid"] = id

  cards[id] = card


with open(f"{csv_path[:-4]}.json", "w") as f:
  json.dump(cards, f, indent=4)

