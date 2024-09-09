# Fireplace Rock 2
Deceptively simple and insanely fun. Welcome to fireplacerock2, the strategy card game that's easy to learn and satisfying to master!

## How to play

Generally follows Hearthstone mechanics. All cards cost mana, and monsters have
an attack and health. When a monster attacks another, they both take battle damage
equal to the other's attack. You can also attack your opponent directly. The first
player to 0 hp loses.

Players alternate turns. You cannot play anything on your opponent's turn.

Each turn consists of the following phase:

Draw - You gain 1 max mana, restore your mana to full, and draw a card.

Main - You can summon monsters or play spells.

Battle - You can attack with your monsters.

Main2 - You can summon monsters or play spells.

There are also two additional phases Standby and End, where mandatory begin/end
of turn effects may happen but the player cannot take any actions.

## How to host

backend:
```
cd be && python run_server.py
```

frontend:
```
cd fe/fpr
npm install
npm start
```

## todo

px => dp
quick spells
continuous spell
continuous effects

