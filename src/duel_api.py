import random
from callbacks import *


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
    return self.cards.__add__(other.cards)

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
    self.id = 0
    self.mana = 0
    self.mana_max = 0
    self.life = 1000
    self.hand = CardList()
    self.deck = CardList()
    self.board = CardList([None] * 5)
    self.graveyard = CardList()
    self.banished = CardList()

  @property
  def field(self):
    field = []
    for card in self.board:
      if card is not None:
        field.append(card)
    return field

  def take_damage(self, source, amount):
    self.life -= amount

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

  def __init__(self, deck1, deck2, p1_io, p2_io):
    self.p1 = Player()
    self.p2 = Player()

    deck1 = [card.create_instance(self.p1, self.p2, self) for card in deck1]
    self.p1.deck = CardList(deck1).shuffle()
    self.p1.id = 1
    self.p1.io = p1_io

    deck2 = [card.create_instance(self.p2, self.p1, self) for card in deck2]
    self.p2.deck = CardList(deck2).shuffle()
    self.p2.id = 2
    self.p2.io = p2_io

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

    # both players draw 3
    for _ in range(3):
      self.draw(p1)
      self.draw(p2)

    # first player's turn
    self.turn(first=True)

    try:
      while True:
        self.turn()
    except GameOver as e:
      if e.winner == 0:
        # draw
        self.p1.io.game_over(0)
        self.p2.io.game_over(0)
      else:
        winner = self.p1 if e.winner == 1 else self.p2
        loser = self.p2 if e.winner == 1 else self.p1
        winner.io.game_over(1)
        loser.io.game_over(-1)


  def turn(self, first=False):
    self.start_turn(first)

    self.draw_phase(first)
    self.standby_phase()

    self.main_phase()

    if not first:
      self.battle_phase()
      self.main_phase(main_phase_2=True)

    self.end_phase()

    self.end_turn()

  def start_turn(self, first=False):
    self.check_game_over()
    self.turn_p.mana_max += 1
    self.turn_p.mana = self.turn_p.mana_max

  def end_turn(self):
    for card in self.turn_p.board:
      if card:
        card.on_end_turn()
    for card in self.other_p.board:
      if card:
        card.on_end_turn()

    self.check_game_over()

    self.cur_turn = 3 - self.cur_turn
    self.turn_p = self.p1 if self.cur_turn == 1 else self.p2
    self.other_p = self.p2 if self.cur_turn == 1 else self.p1


  def draw_phase(self, first):
    self.cur_phase = "draw"

    # draw card
    if not first:
      if not self.turn_p.deck:
        raise GameOver(3 - self.cur_turn)
      self.draw(self.turn_p)

    self.turn_p.io.draw_phase_prompt()

    self.phase_effects()


  def standby_phase(self):
    self.cur_phase = "standby"
    self.phase_effects()


  def main_phase(self, main_phase_2=False):
    if main_phase_2:
      self.cur_phase = "main_2"
    else:
      self.cur_phase = "main"
    self.phase_effects()

    while True:
      response = self.turn_p.io.main_phase_prompt(main_phase_2)
      try:
        match response:
          case ["pass"]:
            break
          case ["summon", hand_idx, board_idx]:
            card = self.play_hand(hand_idx)
            self.summon(card, board_idx)
          case ["activate_hand", hand_idx]:
            pass
            # TODO
          case ["activate_board", board_idx]:
            card = self.turn_p.board[board_idx]
            self.activate_board(card)
          case [other, *_] | [other]:
            raise UnrecognizedCommand(other)
      except UnrecognizedCommand as e:
        self.turn_p.io.display_message(f"Unrecognized command: {e.message}")
      except InvalidMove as e:
        self.turn_p.io.display_message(f"Illegal Move: {e.message}")
      self.check_field()
      self.check_game_over()
    self.phase_effects("end")


  def battle_phase(self):
    self.cur_phase = "battle"
    self.phase_effects()

    while True:
      response = self.turn_p.io.battle_phase_prompt()
      try:
        match response:
          case ["pass"]:
            break
          case ["attack", attacker_idx, attackee_idx]:
            self.attack(attacker_idx, attackee_idx)
          case ["attack_directly", attacker_idx]:
            self.attack_directly(attacker_idx)
            # TODO
          # QUICK EFFECTS ONLY
          # case ["activate_hand", hand_idx]:
          #   pass
            # TODO
          # case ["activate_board", board_idx]:
           #  pass
            # TODO
          case [other, *_] | [other]:
            raise UnrecognizedCommand(other)
      except UnrecognizedCommand as e:
        self.turn_p.io.display_message(f"Unrecognized command: {e.message}")
      except InvalidMove as e:
        self.turn_p.io.display_message(f"Illegal Move: {e.message}")
      self.check_field()
      self.check_game_over()
    self.phase_effects("end")

  def end_phase(self):
    self.cur_phase = "end"
    self.phase_effects()
    self.check_field()
    self.check_game_over()


  def check_game_over(self):
    if self.turn_p.life <= 0 and self.other_p.life <= 0:
      raise GameOver(0)
    if self.turn_p.life <= 0:
      raise GameOver(self.turn_p.id)
    if self.other_p.life <= 0:
      raise GameOver(self.other_p.id)

  def check_field(self, source=None):
    to_remove_turn = []
    to_remove_other = []
    for i, card in enumerate(self.turn_p.board):
      if card is None:
        continue
      if card.health <= 0:
        card.effect("if_destroyed", source)
        card.effect("opt_if_destroyed_cost", source)
        card.effect("opt_if_destroyed", source)
        to_remove_turn.append(i)

    for i, card in enumerate(self.other_p.board):
      if card is None:
        continue
      if card.health <= 0:
        card.effect("if_destroyed", source)
        card.effect("opt_if_destroyed_cost", source)
        card.effect("opt_if_destroyed", source)
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
      self.turn_p.graveyard.append(card)
    for card in other_removed:
      self.other_p.graveyard.append(card)

    for card in turn_removed:
      card.effect("if_send_graveyard")
    for card in other_removed:
      card.effect("if_send_graveyard")

    for card in turn_removed:
      card.effect("opt_if_send_graveyard")
    for card in other_removed:
      card.effect("opt_if_send_graveyard")



  def phase_effects(self, timing="begin"):
    phase = self.cur_phase
    # mandatory standby phase effects
    for card in self.turn_p.board:
      if card:
        card.effect(f"{timing}_phase_{phase}")
        self.check_field()

    for card in self.other_p.board:
      if card:
        card.effect(f"{timing}_phase_{phase}")
        self.check_field()

    # optional standby phase effects
    for card in self.turn_p.board:
      if card:
        card.effect(f"opt_{timing}_phase_{phase}")
        self.check_field()

    for card in self.other_p.board:
      if card:
        card.effect(f"opt_{timing}_phase_{phase}")
        self.check_field()
    self.check_game_over()

  ### CARD ACTIONS ###
  # All of these functions accept a player ["turn", "other"] to bind the
  # effect to (ie., which player did it)

  def play_hand(self, hand_idx, player="turn"):
    active = self.get_active_player(player)

    if hand_idx < 0 or hand_idx >= len(active.hand):
      raise InvalidMove("Invalid hand index")

    card = active.hand[hand_idx]

    if active.can_pay(card.cost):
      active.pay(card.cost)
    else:
      raise InvalidMove("Not enough mana")

    active.hand.remove(hand_idx)
    return card

  def summon(self, card, board_idx, player="turn"):
    if type(player) == str:
      active = self.get_active_player(player)
    else:
      active = player

    if board_idx < 0 or board_idx >= len(active.board):
      raise InvalidMove("Invalid board index")

    if active.board[board_idx] is not None:
      raise InvalidMove("Cannot summon; board occupied")

    active.board[board_idx] = card

    card.reset_stats()

    card.effect("if_summon_cost")
    card.effect("if_summon")
    act = card.effect("opt_if_summon_cost")
    if act:
      card.effect("opt_if_summon")


  def activate_board(self, card, player="turn"):
    if card is None:
      raise InvalidMove("Cannot activate effect; no monster")
    if not card.can("activate"):
      raise InvalidMove("Card cannot activate effect")

    card.effect("on_activate_cost")
    card.effect("on_activate")



  def deck_to_hand(self, card):
    card.owner.deck.remove(card).shuffle()
    card.owner.hand.add(card)


  def send_graveyard(self, card):
    return self.send_graveyard_multiple([card])


  def bounce(self, card):
    if card is None:
      return

    card.owner.board.delete(card)
    card.owner.hand.add(card)
    card.reset_stats()

  def draw(self, player):
    player.hand.append(player.deck.pop()).sort()

  def remove_field(self, card):
    if card is None:
      return
    card.owner.board.delete(card)

  def remove_graveyard(self, card):
    if card is None:
      return
    card.owner.graveyard.remove(card)

  def destroy(self, card):
    return self.destroy_multiple([card])

  def send_graveyard_multiple(self, cards):
    for card in cards:
      if card is None:
        continue
      card.owner.graveyard.append(card)

    for card in cards:
      if card is None:
        continue
      card.effect("if_send_graveyard")
      card.effect("opt_if_send_graveyard")


  def destroy_multiple(self, cards):
    active = self.get_active_player("turn")
    inactive = self.get_inactive_player("turn")

    for card in cards:
      # delete is a no-op if card isn't on the board
      card.owner.board.delete(card)

    # destroyed effects
    for card in cards:
      if card is not None and card.owner == self.turn_p:
        card.effect("if_destroyed")
    for card in cards:
      if card is not None and card.owner == self.other_p:
        card.effect("if_destroyed")
    for card in cards:
      if card is not None and card.owner == self.turn_p:
        card.effect("opt_if_destroyed")
    for card in cards:
      if card is not None and card.owner == self.other_p:
        card.effect("opt_if_destroyed")

    self.send_graveyard_multiple(cards)


  def activate_on_board(self, board_idx, player="turn"):
    active = self.get_active_player(player)
    card = active.board[board_idx]

    if not attacker.can("activate"):
      raise InvalidMove("Selected monster can't activate its effect")

    card.effect("on_activate_cost")
    card.effect("on_activate_effect")


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

    if not attacker.can("attack_directly"):
      raise InvalidMove("Selected monster can't attack")

    attacker.effect("if_attack_directly")
    attacker.effect("opt_if_attack_directly")

    # damage calc
    forward = attacker.effect("attacker_direct_damage_calc")

    inactive.life -= forward

    attacker.effect("end_attack_directly")
    attacker.effect("opt_end_attack_directly")

    attacker.apply_status("god", "CANNOT_ATTACK", 0, "END")

    self.check_game_over()


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

    if not attacker.can("attack"):
      raise InvalidMove("Selected monster can't attack")

    # start step
    attacker.effect("if_attack", attackee)
    attackee.effect("if_attacked", attacker)

    # enter damage step
    # TODO

    # damage calculation
    forward = attacker.effect("attacker_damage_calc", attackee)
    forward = attackee.effect("attackee_damage_calc", attacker, forward)

    backward = attackee.effect("defender_damage_calc", attacker)
    backward = attacker.effect("defendee_damage_calc", attackee, backward)

    attackee.take_damage("battle", forward)
    attacker.take_damage("battle", backward)

    # exit damage step
    # TODO

    # check if things are destroyed
    # (do this bc even if a party heals)
    attackee_destroyed = attackee.health <= 0
    attacker_destroyed = attacker.health <= 0

    # remove cards from field
    if attacker_destroyed:
      active.board.delete(attacker)
    if attackee_destroyed:
      inactive.board.delete(attackee)

    # attacker effects
    if attackee_destroyed:
      attacker.effect("if_destroy_battle", attackee)
    if attacker_destroyed:
      attacker.effect("if_destroyed_battle", attackee)
      attacker.effect("if_destroyed")
    # attackee effects
    if attacker_destroyed:
      attackee.effect("if_destroy_battle", attacker)
    if attackee_destroyed:
      attackee.effect("if_destroyed_battle", attacker)
      attackee.effect("if_destroyed", attackee)
    # optional attacker effects
    if attackee_destroyed:
      attacker.effect("opt_if_destroy_battle", attackee)
    if attacker_destroyed:
      attacker.effect("opt_if_destroyed_battle", attackee)
      attacker.effect("opt_if_destroyed")
    # optional attackee effects
    if attacker_destroyed:
      attackee.effect("opt_if_destroy_battle", attacker)
    if attackee_destroyed:
      attackee.effect("opt_if_destroyed_battle", attacker)
      attackee.effect("opt_if_destroyed", attackee)

    # send cards to graveyard
    to_gy = []
    if attacker_destroyed:
      to_gy.append(attacker)
    if attackee_destroyed:
      to_gy.append(attackee)
    self.send_graveyard_multiple(to_gy)

    attacker.effect("end_attack", attackee)
    attackee.effect("end_attacked", attacker)

    attacker.effect("opt_end_attack", attackee)
    attackee.effect("opt_end_attacked", attacker)

    attacker.apply_status("god", "CANNOT_ATTACK", 0, "END")

    self.check_game_over()



