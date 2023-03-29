import sys
import pandas as pd
import json

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
  card["cost"] = row["Cost"]
  if card["type"] == "Monster":
    card["attack"] = row["Attack"]
    card["health"] = row["Health"]
  if row["Flavour"]:
    card["flavour"] = row["Flavour"]
  if row["Description"]:
    card["description"] = row["Description"]
  else:
    card["description"] = ""
  card["id"] = row["ID"]
  card["rarity"] = row["Rarity"]

  id = row["Name"].lower()
  id = ''.join(ch for ch in id if ch.isalnum())
  card["uuid"] = id

  cards[id] = card


with open(f"{csv_path[:-4]}.json", "w") as f:
  json.dump(cards, f, indent=4)

