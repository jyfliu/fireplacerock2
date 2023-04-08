import random
from callbacks import *


class Graveyard():

  def __init__(self):
    self.cards = []

  def __contains__(self, card):
    return card in self.cards

  def __len__(self):
    return len(self.cards)

  def filter(self, fn):
    return [card for card in self.cards if fn(card)]

  def contains(self, fn):
    return len(self.filter(fn)) > 0

  def add(self, card):
    self.cards.append(card)

  def remove(self, card):
    # TODO
    pass


class Player():

  def __init__(self):
    self.id = 0
    self.mana = 0
    self.mana_max = 0
    self.life = 1000
    self.hand = []
    self.deck = []
    self.board = [None] * 5
    self.graveyard = Graveyard()

  @property
  def field(self):
    field = []
    for card in self.board:
      if card is not None:
        field.append(card)
    return field

  def can_pay(self, amount):
    return self.mana >= amount

  def pay(self, amount):
    assert self.mana >= amount
    self.mana -= amount

  def hand_str(self):
    return " | ".join(
        [f"{str(c)[:24]: <24}" for c in self.hand]
    )

  def board_str(self):
    return " | ".join(
        [f"{str(c)[:24]: <24}" if c is not None else " "*24 for c in self.board]
    )


class Duel():

  def __init__(self, deck1, deck2, io):
    self.p1 = Player()
    self.p2 = Player()

    deck1 = [card.create_instance(self.p1, self.p2, self) for card in deck1]
    self.p1.deck = random.sample(deck1, k=len(deck1))
    self.p1.id = 1

    deck2 = [card.create_instance(self.p2, self.p1, self) for card in deck2]
    self.p2.id = 2
    self.p2.deck = random.sample(deck2, k=len(deck2))

    self.io = io

  ### HELPER FUNCTIONS ###
  def get_active_player(self, player):
    if player == "turn":
      return self.turn_p
    elif player == "other":
      return self.other_p

  def get_inactive_player(self, player):
    if player == "turn":
      return self.other_p
    elif player == "other":
      return self.turn_p

  ### MANDATORY STUFF ###

  def start_duel(self):
    if random.random() < 0.5:
      # randomize who is going first
      self.turn_p = self.p1
      self.other_p = self.p2
      self.cur_turn = 1
    else:
      self.turn_p = self.p2
      self.other_p = self.p1
      self.cur_turn = 2

    p1 = self.turn_p
    p2 = self.other_p

    p1.hand = p1.deck[-3:]
    p1.deck = p1.deck[:-3]
    p2.hand = p2.deck[-3:]
    p2.deck = p2.deck[:-3]


  def end_turn(self):
    self.end_phase()

    for card in self.turn_p.board:
      if card:
        card.end_turn()
    for card in self.other_p.board:
      if card:
        card.end_turn()

    self.cur_turn = 3 - self.cur_turn
    self.turn_p = self.p1 if self.cur_turn == 1 else self.p2
    self.other_p = self.p2 if self.cur_turn == 1 else self.p1


  def start_turn(self, first=False):
    self.turn_p.mana_max += 1
    self.turn_p.mana = self.turn_p.mana_max

    self.draw_phase(first)
    self.standby_phase()


  def draw_phase(self, first):
    self.cur_phase = "draw"
    if not first:
      if not self.turn_p.deck:
        raise GameOver(3 - self.cur_turn)
      self.turn_p.hand += self.turn_p.deck[-1:]
      self.turn_p.deck = self.turn_p.deck[:-1]

    for card in self.turn_p.board:
      if card:
        card.on_draw()

    for card in self.other_p.board:
      if card:
        card.on_draw()

  def standby_phase(self):
    self.cur_phase = "standby"
    for card in self.turn_p.board:
      if card:
        card.on_standby()

    for card in self.other_p.board:
      if card:
        card.on_standby()

  def main_phase(self):
    self.cur_phase = "main"

  def end_phase(self):
    self.cur_phase = "end"
    for card in self.turn_p.board:
      if card:
        card.on_end()
    for card in self.other_p.board:
      if card:
        card.on_end()


  def update_board(self):
    if self.turn_p.life <= 0:
      raise GameOver(self.turn_p.id)
    if self.other_p.life <= 0:
      raise GameOver(self.other_p.id)

    # activate on destroy effects
    to_remove_turn = []
    to_remove_other = []
    for i, card in enumerate(self.turn_p.board):
      if card is None:
        continue
      if card.health <= 0:
        card.on_destroyed()
        to_remove_turn.append(i)

    for i, card in enumerate(self.other_p.board):
      if card is None:
        continue
      if card.health <= 0:
        card.on_destroyed()
        to_remove_other.append(i)

    # remove cards from field
    turn_removed = []
    other_removed = []
    for i in to_remove_turn:
      turn_removed.append(self.turn_p.board[i])
      self.turn_p.board[i] = None
    for i in to_remove_other:
      other_removed.append(self.other_p.board[i])
      self.other_p.board[i] = None

    # send cards to graveyard
    for card in turn_removed:
      self.send_graveyard(card, player="turn", update_board=False)
    for card in other_removed:
      self.send_graveyard(card, player="other", update_board=False)

    if self.turn_p.life <= 0:
      raise GameOver(self.turn_p.id)
    if self.other_p.life <= 0:
      raise GameOver(self.other_p.id)


  ### IO ###
  # stuff the frontend must implement

  def can_target_other_field(self, player="turn"):
    inactive = self.get_inactive_player(player)
    for card in inactive.board:
      if card is not None:
        return True
    return False


  def target_other_field(self, player="turn"):
    if self.can_target_other_field(player):
      idx = self.io.target_other_field(player)

      inactive = self.get_inactive_player(player)
      card = inactive.board[idx]
      return card
    else:
      raise InvalidMove("No valid targets")

  def target_field(self, player="turn"):
    raise NotImplemented()

  def flip_coin(self, player="turn"):
    coin = random.randint(0, 1)
    self.io.flip_coin(coin, player)
    return coin

  def get_adjacent(self, card, player="turn"):
    active = self.get_active_player(turn)
    for i, c in enumerate(active.board):
      if c == card:
        break
    else: # for else
      return []

    adjs = []
    if i > 0 and active.board[i - 1]:
      adjs.append(active.board[i - 1])
    if i < len(active.board) - 1 and active.board[i + 1]:
      adjs.append(active.board[i + 1])

    return adjs


  ### CARD ACTIONS ###
  # All of these functions accept a player ["turn", "other"] to bind the
  # effect to (ie., which player did it)

  def play_hand(self, hand_idx, player="turn"):
    active = self.get_active_player(player)

    if hand_idx < 0 or hand_idx >= len(active.hand):
      raise InvalidMove("Invalid hand index")

    card = active.hand[hand_idx]

    if card.cost <= active.mana:
      active.mana -= card.cost
    else:
      raise InvalidMove("Not enough mana")

    del active.hand[hand_idx]
    return card

  def summon(self, card, board_idx, player="turn"):
    if type(player) == "str":
      active = self.get_active_player(player)
    else:
      active = player

    if board_idx < 0 or board_idx >= len(active.board):
      raise InvalidMove("Invalid board index")

    if active.board[board_idx] is not None:
      raise InvalidMove("Cannot summon; board occupied")

    active.board[board_idx] = card
    card.on_summon()

    self.update_board()

  def remove_field(self, card, player="turn"):
    if card is None:
      return

    active = self.get_active_player(player)
    remove_idxs = []
    for i, c in enumerate(active.board):
      if c == card:
        remove_idxs.append(i)
    for i in remove_idxs:
      active.board[i] = None


  def send_graveyard(self, card, player="turn", update_board=True):
    if card is None:
      return

    player = self.get_active_player(player)
    player.graveyard.append(card)
    card.on_send_graveyard()

    if update_board:
      self.update_board()

  def activate_on_board(self, board_idx, player="turn"):
    active = self.get_active_player(player)
    card = active.board[board_idx]

    card.on_activate()

    self.update_board()

  def attack_directly(self, attacker_idx, player="turn"):
    active = self.get_active_player(player)
    inactive = self.get_inactive_player(player)

    for card in inactive.board:
      if card is not None:
        raise InvalidMove("Field is not empty")

    if (
        attacker_idx < 0
        or attacker_idx >= len(active.board)
        or active.board[attacker_idx] is None
    ):
      raise InvalidMove("Invalid attacker index")

    attacker = active.board[attacker_idx]

    if not attacker.can_attack():
      raise InvalidMove("Selected monster can't attack")

    attacker.on_attack_directly()
    inactive.life -= attacker.attack

    attacker.status.append(("CANNOT_ATTACK", 0, "END"))

    self.update_board()


  def attack(self, attacker_idx, attackee_idx, player="turn"):
    active = self.get_active_player(player)
    inactive = self.get_inactive_player(player)

    if (
        attacker_idx < 0
        or attacker_idx >= len(active.board)
        or active.board[attacker_idx] is None
    ):
      raise InvalidMove("Invalid attacker index")
    if (
        attackee_idx < 0
        or attackee_idx >= len(inactive.board)
        or inactive.board[attackee_idx] is None
    ):
      raise InvalidMove("Invalid attackee index")

    attacker = active.board[attacker_idx]
    attackee = inactive.board[attackee_idx]

    if not attacker.can_attack():
      raise InvalidMove("Selected monster can't attack")

    amount = attacker.on_attack(attackee)
    amount = attackee.on_attacked(attacker, amount)

    attackee.health -= amount

    amount = attacker.on_take_battle_damage(attackee.attack)
    amount = attacker.on_take_damage(amount)
    attacker.health -= amount

    attacker.end_attack(attackee)
    attackee.end_attacked(attacker)

    if attackee.health <= 0:
      attacker.on_destroy_battle()
      attackee.on_destroyed_battle()
    if attacker.health <= 0:
      attackee.on_destroy_battle()
      attacker.on_destroyed_battle()

    attacker.status.append(("CANNOT_ATTACK", 0, "END"))

    self.update_board()


