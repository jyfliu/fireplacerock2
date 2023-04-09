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
    p1.hand.extend(p1.deck.pop(3)).sort()
    p2.hand.extend(p2.deck.pop(3)).sort()

    # first player's turn
    self.turn(first=True)

    while True:
      self.turn()

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
    self.turn_p.mana_max += 1
    self.turn_p.mana = self.turn_p.mana_max

  def end_turn(self):
    for card in self.turn_p.board:
      if card:
        card.on_end_turn()
    for card in self.other_p.board:
      if card:
        card.on_end_turn()

    self.cur_turn = 3 - self.cur_turn
    self.turn_p = self.p1 if self.cur_turn == 1 else self.p2
    self.other_p = self.p2 if self.cur_turn == 1 else self.p1


  def draw_phase(self, first):
    self.cur_phase = "draw"

    # draw card
    if not first:
      if not self.turn_p.deck:
        raise GameOver(3 - self.cur_turn)
      self.turn_p.hand.append(self.turn_p.deck.pop()).sort()

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
          pass
          # TODO
        case [other, *_] | [other]:
          raise UnrecognizedCommand(other)
      self.check_field()
    self.phase_effects("end")


  def battle_phase(self):
    self.cur_phase = "battle"
    self.phase_effects()

    while True:
      response = self.turn_p.io.battle_phase_prompt()
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
      self.check_field()
    self.phase_effects("end")

  def end_phase(self):
    self.cur_phase = "end"
    self.phase_effects()


  def check_game_over(self):
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


  ### IO ###

  def prompt_user_activate(self, effect_name, player="turn"):
    active = self.get_active_player(player)
    return active.io.prompt_user_activate(effect_name)

  def can_target_other_field(self, player="turn"):
    inactive = self.get_inactive_player(player)
    for card in inactive.board:
      if card is not None:
        return True
    return False


  def target_other_field(self, player="turn"):
    if self.can_target_other_field(player):
      active = self.get_active_player(player)
      idx = active.io.target_other_field(player)

      inactive = self.get_inactive_player(player)
      card = inactive.board[idx]
      return card
    else:
      raise InvalidMove("No valid targets")

  def target_field(self, player="turn"):
    raise NotImplemented()

  def flip_coin(self, player="turn"):
    coin = random.randint(0, 1)
    active = self.get_active_player(player)
    active.io.flip_coin(coin, player)
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

  # TEMP STUFF

  def target_owner_board_empty(self):
    raise

  def target_other_board_empty(self):
    raise

    # target card on the field
    # optionally accepts a lambda to filter
    # returns card of monster
  def target_field(self):
    raise

  def target_owner_field(self):
    pass

  def select_field(self):
    raise

  def select_owner_field(self):
    raise

  def select_other_field(self):
    raise


    # select card from deck
    # optionally accepts a lambda to filter
    # returns card
  def select_owner_deck(self):
    raise

    # select_other_deck = self.io.select_other_deck

    # select card from deck
    # optionally accepts a lambda to filter
    # returns card
  def select_owner_graveyard(self):
    raise

  def select_other_graveyard(self):
    raise






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

    card.effect("if_summon_cost")
    card.effect("if_summon")
    act = card.effect("opt_if_summon_cost")
    if act:
      card.effect("opt_if_summon")

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


  def send_graveyard(self, card, player="turn"):
    if card is None:
      return

    player = self.get_active_player(player)
    player.graveyard.append(card)
    card.effect("if_send_graveyard")
    card.effect("opt_if_send_graveyard")


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
    inactive.life -= attacker.attack

    attacker.status.append(("CANNOT_ATTACK", 0, "END"))

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

    # remove cards from field
    if attacker_destroyed:
      active.board.delete(attacker)
    if attackee_destroyed:
      inactive.board.delete(attackee)

    # send cards to graveyard
    if attacker_destroyed:
      self.send_graveyard(attacker, player="turn")
    if attackee_destroyed:
      self.send_graveyard(attackee, player="other")

    attacker.effect("end_attack", attackee)
    attackee.effect("end_attacked", attacker)

    attacker.effect("opt_end_attack", attackee)
    attackee.effect("opt_end_attacked", attacker)

    attacker.status.append(("CANNOT_ATTACK", 0, "END"))

    self.check_game_over()



