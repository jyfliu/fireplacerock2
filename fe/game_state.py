class Card:

  def __init__(self, card):
    self.name = card.name
    self.cost = card.cost
    self.type = card.type
    if self.type == "monster":
      self.attack = card.attack
      self.health = card.health
      self.original_attack = card.original_attack
      self.original_health = card.original_health
    self.status = []

    self.uuid = card.uuid
    self.description = card.description
    self.flavour = card.flavour

  def __eq__(self, other):
    if other is None:
      return False
    return self.uuid == other.uuid

  def __str__(self):
    if self.type == "monster":
      return f"{self.name} {self.cost} {self.attack}/{self.health}"
    else:
      return f"{self.name} {self.cost}"


class CardList:

  def __init__(self, cards=None):
    if cards:
      self.cards = cards
    else:
      self.cards = []

  def __contains__(self, card):
    return card in self.cards

  def __len__(self):
    return len(self.cards)

  def __getitem__(self, *args):
    return self.cards.__getitem__(*args)

  def __setitem__(self, *args):
    return self.cards.__setitem__(*args)

  def __add__(self, other):
    return CardList(self.cards.__add__(other.cards))

  def filter(self, fn):
    return CardList([card for card in self.cards if card is not None and fn(card)])

  def contains(self, fn):
    for card in self.cards:
      if card is None:
        continue
      if fn(card):
        return True
    return False

  def add(self, card):
    self.cards.append(card)
    return self

  def append(self, card):
    self.cards.append(card)
    return self

  def extend(self, lst2):
    if type(lst2) == list:
      self.cards.extend(lst2)
    else:
      self.cards.extend(lst2.cards)
    return self

  def pop(self, amount=1):
    if amount == 1:
      to_pop = self.cards[-1]
      self.cards = self.cards[:-1]
      return to_pop
    to_pop = self.cards[-amount:]
    self.cards = self.cards[:-amount]
    return to_pop

  def shuffle(self):
    self.cards = random.sample(self.cards, k=len(self.cards))
    return self

  def sort(self):
    self.cards.sort(key=lambda card: (card.type, card.cost, card.name))
    return self

  def remove(self, card):
    if type(card) == int:
      del self.cards[card]
    else:
      self.cards = [c for c in self.cards if c != card]
    return self

  def delete(self, card):
    self.cards = [c if c != card else None for c in self.cards]
    return self


class Player():

  def __init__(self):
    self.mana = 0
    self.mana_max = 0
    self.life = 3000
    self.hand = CardList()
    self.deck = CardList()
    self.extradeck = CardList()
    self.board = CardList([None] * 5)
    self.graveyard = CardList()
    self.banished = CardList()

  @property
  def field(self):
    field = []
    for card in self.board:
      if card is not None:
        field.append(card)
    return CardList(field)

  @property
  def cards(self):
    return self.field + self.hand + self.deck + self.graveyard + self.banished

  def hand_str(self):
    return " | ".join(
        [f"{str(c)[:24]: <24}" for c in self.hand]
    )

  def board_str(self):
    return " | ".join(
        [f"{str(c)[:24]: <24}" if c is not None else " "*24 for c in self.board]
    )

