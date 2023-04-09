import sys
import pandas as pd
import json

triggers = [
  # MANDATORY TURN EFFECTS
  "begin_phase_draw", # after turn player draws a card
  "begin_phase_standby", # "in your standby phase"
  "begin_phase_main", # "at the beginning of main phase"
  "end_phase_main", # "at the end of main phase"
  "begin_phase_battle", # "at the beginning of battle phase"
  "end_phase_battle", # "at the end of battle phase"
  "begin_phase_main_2", # "at the beginning of main phase 2"
  "end_phase_main_2", # "at the end of main phase 2"
  "begin_phase_end", # "in your end phase"
  # OPTIONAL TURN EFFCTS
  "opt_begin_phase_draw", # "in your draw phase you can"
  "opt_begin_phase_standby", # "in your standby phase you can"
  "opt_begin_phase_main", # "at the beginning of main phase you can"
  "opt_end_phase_main", # "at the end of main phase you can"
  "opt_begin_phase_battle", # "at the beginning of battle phase you can"
  "opt_end_phase_battle", # "at the end of battle phase you can"
  "opt_begin_phase_main_2", # "at the beginning of main phase 2 you can"
  "opt_end_phase_main_2", # "at the end of main phase 2 you can"
  "opt_end_phase_end", # "in your end phase you can"
  # CARD EFFECTS
  "can_summon",
  "on_summon", # summoning conditions (eg., tribute), doesn't start chain
  "if_summon_cost", # "if this card is summoned" cost
  "if_summon", # "if this card is summoned" effect
  "if_destroyed", # "if this card is destroyed"
  "if_send_graveyard", # "if this card is sent to the graveyard"
  # OPTIONAL CARD EFFECTS
  "opt_if_summon_cost", # "if this card is summoned" cost
  "opt_if_summon", # "if this card is summoned" effect
  "opt_if_destroyed", # "if this card is destroyed"
  "opt_if_send_graveyard", # "if this card is sent to the graveyard"
  "can_activate",
  "on_activate_cost", # "you can ..." cost
  "on_activate", # "you can ..." effect
  # BATTLE EFFECTS
  "if_destroy_battle", # (other) if this destroys another by battle
  "if_destroyed_battle", # (other)
  "can_attack",
  "can_attack_directly",
  "if_attack", # if this monster is about to attack another monster
  "if_attack_directly", # if this monster is about to attack directly
  "if_attacked", # if this monster is selected for an attack
  "attacker_damage_calc", # (other) => attack damage done
  "attackee_damage_calc", # (other, amount) => attack damage done
  "defender_damage_calc", # (other) => recoil damage done
  "defendee_damage_calc", # (other, amount) => recoil damage done
  "on_take_damage", # if this monster takes damage
  "on_take_battle_damage", # if this monster takes damage from battle
  "end_attack", # (other, damage_dealt)
  "end_attacked", # (other, damage_dealt)
  # OPTIONAL BATTLE EFFECTS
  "opt_if_destroy_battle", # if this destroys another by battle
  "opt_if_destroyed_battle",
  "opt_if_attack", # if this monster is about to attack another monster
  "opt_if_attack_directly", # if this monster is about to attack directly
  "opt_if_attacked", # if this monster is selected for an attack
  "opt_end_attack", # (other, damage_dealt)
  "opt_end_attacked", # (other, damage_dealt)
  # SPELL EFFECTS
  "spell_can_activate",
  "spell_on_activate",
  "spell_on_resolve",
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
  card["type"] = row["Type"].lower()
  card["cost"] = int_or_nothing(row["Cost"])
  if card["type"] == "monster":
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

  for fn, value in row.items():
    if fn in triggers and value:
      card[fn] = value.replace("\\n", "\n")

  id = row["Name"].lower()
  id = ''.join(ch for ch in id if ch.isalnum())
  card["uuid"] = id

  cards[id] = card


with open(f"{csv_path[:-4]}.json", "w") as f:
  json.dump(cards, f, indent=4)

