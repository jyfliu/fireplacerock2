import random
from callbacks import *


class Player():

  def __init__(self):
    self.id = 0
    self.mana = 0
    self.mana_max = 0
    self.life = 300
    self.hand = []
    self.deck = []
    self.board = [None] * 5
    self.graveyard = []

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
    p2.deck = p2.deck[:3]


  def end_turn(self):
    self.cur_turn = 3 - self.cur_turn
    self.turn_p = self.p1 if self.cur_turn == 1 else self.p2
    self.other_p = self.p2 if self.cur_turn == 1 else self.p1


  def start_turn(self, first=False):
    self.turn_p.mana_max += 1
    self.turn_p.mana = self.turn_p.mana_max

    if not first:
      if not self.turn_p.deck:
        raise GameOver(3 - self.cur_turn)
      self.turn_p.hand += self.turn_p.deck[-1:]
      self.turn_p.deck = self.turn_p.deck[:-1]


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
        card.on_destroy()
        to_remove_turn.append(i)

    for i, card in enumerate(self.other_p.board):
      if card is None:
        continue
      if card.health <= 0:
        card.on_destroy()
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


  ### CARD ACTIONS ###
  # All of these functions accept a player ["turn", "other"] to bind the
  # effect to (ie., which player did it)

  def play_hand(self, hand_idx, player="turn"):
    active = self.get_active_player(player)

    card = active.hand[hand_idx]
    if card.mana <= active.mana:
      active.mana -= card.mana
    else:
      raise InvalidMove("Not enough mana")

    del active.hand[hand_idx]
    return card

  def summon(self, card, board_idx, player="turn"):
    active = self.get_active_player(player)

    active.board[board_idx] = card
    card.on_summon()

    self.update_board()

  def send_graveyard(self, card, player="turn", update_board=True):
    player = self.get_active_player(player)
    player.graveyard.append(card)
    card.on_send_graveyard()

    if update_board:
      self.update_board()

  def attack_directly(self, attacker_idx, player="turn"):
    active = self.get_active_player(player)
    inactive = self.get_inactive_player(player)

    for card in inactive.board:
      if card is not None:
        raise InvalidMove("Field is not empty")

    attacker = active.board[attacker_idx]

    attacker.on_attack_directly()
    inactive.life -= attacker.attack

    self.update_board()


  def attack(self, attacker_idx, attackee_idx, player="turn"):
    active = self.get_active_player(player)
    inactive = self.get_inactive_player(player)

    attacker = active.board[attacker_idx]
    attackee = inactive.board[attackee_idx]

    attacker.on_attack(attackee)
    attackee.health -= attacker.attack
    attacker.health -= attackee.attack
    attackee.on_attacked(attacker)

    self.update_board()


