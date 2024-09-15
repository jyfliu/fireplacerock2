import random
from .callbacks import *

from .card_api import hooks, god

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

  def __str__(self):
    return str([card.name for card in self.cards])

  def filter(self, fn):
    return CardList([card for card in self.cards if card is not None and fn(card)])

  def map(self, fn):
    return [fn(card) if card is not None else None for card in self.cards]

  def contains(self, fn):
    for card in self.cards:
      if card is None:
        continue
      if fn(card):
        return True
    return False

  def index_of(self, card):
    for i, c in enumerate(self.cards):
      if c == card:
        return i
    return -1

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
    self.cards.sort(key=lambda card: (card.type, card.cost, card.name, card.uuid))
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

  def to_list(self):
    return [c for c in self.cards if c is not None]


class Player():

  def __init__(self, id, io):
    self.id = id
    self.io = io
    self.mana = 0
    self.mana_max = 0
    self.life = 4000

    self.hand = CardList()
    self.deck = CardList()
    self.extradeck = CardList()
    self.board = CardList([None] * 5)
    self.traps = CardList([None] * 5)
    self.graveyard = CardList()
    self.banished = CardList()

    self.hooks = { hook: [] for hook in hooks }
    self.status = []
    self.oppon = None

  def set_oppon(self, oppon):
    self.oppon = oppon

  @property
  def field(self):
    field = []
    for card in self.board:
      if card is not None:
        field.append(card)
    return CardList(field)

  @property
  def cards(self):
    return self.field + self.hand + self.deck + self.extradeck + self.graveyard + self.banished

  def take_damage(self, source, amount):
    self.life -= amount

    # TODO pass source information (for animations)
    self.io.take_damage(amount)
    self.oppon.io.oppon_take_damage(amount)

  def heal(self, source, amount):
    self.life += amount

    self.io.heal(amount)
    self.oppon.io.oppon_heal(amount)

  def restore_mana(self, new_mana, new_mana_max=-1):
    self.mana = new_mana
    if new_mana_max > 0:
      self.mana_max = new_mana_max
    self.io.restore_mana(new_mana, new_mana_max)
    self.oppon.io.oppon_restore_mana(new_mana, new_mana_max)

  def can_pay(self, amount):
    return self.mana >= amount

  def pay(self, amount):
    assert self.mana >= amount
    self.mana -= amount

    for _, hook in self.hooks["on_owner_pay_mana"]:
      hook(amount)
    for _, hook in self.oppon.hooks["on_oppon_pay_mana"]:
      hook(amount)

    self.io.pay_mana(amount)
    self.oppon.io.oppon_pay_mana(amount)

  def has_status(self, status):
    for st in self.status:
      if st[0] == status:
        return True
    return False

  def get_status(self, status):
    for st in self.status:
      if st[0] == status:
        return st[3]
    return None

  def apply_status(self, source, status, duration=0, expiry="end", args=True):
    self.status.append([status, duration, expiry, args])

  def on_end_turn(self):
    new_status = []
    for st in self.status:
      if st[1] < 0:
        new_status.append(st)
      elif st[1] == 0:
        pass
      else:
        st[1] = st[1] - 1
        new_status.append(st)
    self.status = new_status

  def hand_str(self):
    return " | ".join(
        [f"{str(c)[:24]: <24}" for c in self.hand]
    )

  def board_str(self):
    return " | ".join(
        [f"{str(c)[:24]: <24}" if c is not None else " "*24 for c in self.board]
    )


def entrypoint(inner):
  def modified(self, *args, **kwargs):
    if self.game_running:
      try:
        inner(self, *args, **kwargs)
      except UnrecognizedCommand as e:
        self.turn_p.io.display_message(f"Unrecognized command: {e.message}")
      except InvalidMove as e:
        self.turn_p.io.display_message(f"Illegal Move: {e.message}")
      except GameOver as e:
        self._handle_game_over(e)
    else:
      self.turn_p.io.display_message("Game not running.")
  return modified


class Duel():

  def __init__(self, card_templates, deck1, deck2, p1_io, p2_io):
    self.card_templates = card_templates

    self.p1 = Player(1, p1_io)
    self.p2 = Player(2, p2_io)

    p1_io.connect(self, self.p1)
    p2_io.connect(self, self.p2)

    self.p1.set_oppon(self.p2)
    self.p2.set_oppon(self.p1)

    deck1, extradeck1 = deck1
    deck2, extradeck2 = deck2

    deck1 = [card.create_instance(self.p1, self.p2, self) for card in deck1]
    self.p1.deck = CardList(deck1).shuffle()

    deck2 = [card.create_instance(self.p2, self.p1, self) for card in deck2]
    self.p2.deck = CardList(deck2).shuffle()

    extradeck1 = [card.create_instance(self.p1, self.p2, self) for card in extradeck1]
    self.p1.extradeck = CardList(extradeck1).sort()

    extradeck2 = [card.create_instance(self.p2, self.p1, self) for card in extradeck2]
    self.p2.extradeck = CardList(extradeck2).sort()

    self.cur_phase = "unknown"
    self.game_running = True

    p1_io.game_start()
    p2_io.game_start()

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

  def get_card(self, card_id):
    for card in self.turn_p.cards + self.other_p.cards:
      if card.uuid == card_id:
        return card
    self.turn_p.io.display_message(f"Internal Error 332: card {card_id} not found")
    self.other_p.io.display_message(f"Internal Error 332: card {card_id} not found")

  def has_initiative(self, player):
    # are we actively waiting for an input from this player
    # temporarily just set to true if its players turn
    return self.turn_p == player


  ### MANDATORY STUFF ###

  @entrypoint
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

    # init extra decks
    for p in [self.turn_p, self.other_p]:
      p.io.init_game_state(
          owner_player=p,
          oppon_player=p.oppon,
      )

    # both players draw 4
    for _ in range(4):
      self.draw(self.turn_p)
      self.draw(self.other_p)

    self.is_first_turn = True
    self.start_turn()
    self.draw_phase()


  def start_turn(self):
    self.check_game_over()
    self.turn_p.restore_mana(self.turn_p.mana_max + 1, self.turn_p.mana_max + 1)

  def end_cur_phase(self):
    match self.cur_phase:
      case "draw":
        self.standby_phase()
      case "standby":
        self.main_phase()
      case "main":
        self.phase_effects("end")
        if not self.is_first_turn:
          self.battle_phase()
        else:
          self.end_phase()
      case "battle":
        self.phase_effects("end")
        self.main_phase(main_phase_2=True)
      case "main_2":
        self.phase_effects("end")
        self.end_phase()
      case "end":
        self.end_turn()
        self.start_turn()
        self.draw_phase()

  def end_turn(self):
    for card in self.turn_p.cards:
      if card:
        card.on_end_turn()
    for card in self.other_p.cards:
      if card:
        card.on_end_turn()

    self.turn_p.on_end_turn()
    self.other_p.on_end_turn()
    self.turn_p.io.end_turn()
    self.other_p.io.end_turn()
    self.check_game_over()

    self.cur_turn = 3 - self.cur_turn
    self.turn_p = self.p1 if self.cur_turn == 1 else self.p2
    self.other_p = self.p2 if self.cur_turn == 1 else self.p1

    self.is_first_turn = False

  def draw_phase(self):
    self.cur_phase = "draw"

    # draw card
    if not self.is_first_turn:
      if not self.turn_p.deck:
        raise GameOver(3 - self.cur_turn)
      self.draw(self.turn_p)

    self.turn_p.io.begin_phase("owner", self.cur_phase)
    self.other_p.io.begin_phase("oppon", self.cur_phase)

    self.phase_effects()

    self.turn_p.io.wait_input(spell_speed=2)


  def standby_phase(self):
    self.cur_phase = "standby"

    self.turn_p.io.begin_phase("owner", self.cur_phase)
    self.other_p.io.begin_phase("oppon", self.cur_phase)

    self.phase_effects()

    self.turn_p.io.wait_input(spell_speed=2)


  def main_phase(self, main_phase_2=False):
    if main_phase_2:
      self.cur_phase = "main_2"
    else:
      self.cur_phase = "main"

    self.turn_p.io.begin_phase("owner", self.cur_phase)
    self.other_p.io.begin_phase("oppon", self.cur_phase)

    self.phase_effects()

    self.turn_p.io.wait_input(spell_speed=1)

  @entrypoint
  def player_action(self, player_id, action):
    if player_id != self.cur_turn:
      # raise InvalidMove("quick effects not implemented")
      return
    # if self.has_initiative(player)
    match action:
      case ["pass"]:
        self.end_cur_phase()

      case ["summon", hand_idx, board_idx]:
        if not "main" in self.cur_phase:
          raise InvalidMove("Not in main phase")
        card = self.play_hand(hand_idx, action="summon")
        self.summon(card, board_idx)

      case ["summon_extradeck", extradeck_idx, board_idx]:
        if not "main" in self.cur_phase:
          raise InvalidMove("Not in main phase")
        card = self.play_extradeck(extradeck_idx)
        self.summon(card, board_idx)

      case ["activate_spell", hand_idx, board_idx]:
        if not "main" in self.cur_phase:
          raise InvalidMove("Not in main phase")
        card = self.play_hand(hand_idx, action="activate_hand")
        self.activate_spell(card, board_idx)

      case ["activate_board", board_idx]:
        if not "main" in self.cur_phase:
          raise InvalidMove("Not in main phase")
        card = self.turn_p.board[board_idx]
        self.activate_board(card)

      case ["activate_field_spell", trap_idx]:
        if not "main" in self.cur_phase:
          raise InvalidMove("Not in main phase")
        card = self.turn_p.traps[trap_idx]
        self.activate_board(card)

      case ["attack", attacker_idx, attackee_idx]:
        if not self.cur_phase == "battle":
          raise InvalidMove("Not in battle phase")
        self.attack(attacker_idx, attackee_idx)

      case ["attack_directly", attacker_idx]:
        if not self.cur_phase == "battle":
          raise InvalidMove("Not in battle phase")
        self.attack_directly(attacker_idx)

      case [other, *_] | [other]:
        raise UnrecognizedCommand(other)

    self.check_field()
    self.check_game_over()


  def battle_phase(self):
    self.cur_phase = "battle"

    self.turn_p.io.begin_phase("owner", self.cur_phase)
    self.other_p.io.begin_phase("oppon", self.cur_phase)

    self.phase_effects()

    self.turn_p.io.wait_input(spell_speed=1)


  def end_phase(self):
    self.cur_phase = "end"

    self.turn_p.io.begin_phase("owner", self.cur_phase)
    self.other_p.io.begin_phase("oppon", self.cur_phase)

    self.phase_effects()
    self.check_field()
    self.check_game_over()


  def check_game_over(self):
    if self.turn_p.life <= 0 and self.other_p.life <= 0:
      raise GameOver(0)
    if self.turn_p.life <= 0:
      raise GameOver(self.other_p.id)
    if self.other_p.life <= 0:
      raise GameOver(self.turn_p.id)


  def _handle_game_over(self, e):
    self.game_running = False
    if e.winner == 0:
      # draw
      self.p1.io.game_over(0)
      self.p2.io.game_over(0)
    else:
      winner = self.p1 if e.winner == 1 else self.p2
      loser = self.p2 if e.winner == 1 else self.p1
      winner.io.game_over(1)
      loser.io.game_over(-1)


  def check_field(self, source=None):
    to_gy = []
    for i, card in enumerate(self.turn_p.board):
      if card is None:
        continue
      if card.health <= 0:
        to_gy.append(card)

    for i, card in enumerate(self.other_p.board):
      if card is None:
        continue
      if card.health <= 0:
        to_gy.append(card)

    for card in to_gy:
      card.effect("if_destroyed", source)
    for card in to_gy:
      for _, hook in card.owner.hooks["on_owner_destroyed"]:
        hook(card)
    for card in to_gy:
      for _, hook in card.oppon.hooks["on_oppon_destroyed"]:
        hook(card)
    for card in to_gy:
      card.effect("opt_if_destroyed", source)

    self.send_graveyard_multiple(to_gy)


  def phase_effects(self, timing="begin"):
    phase = self.cur_phase
    # mandatory phase effects
    for card in self.turn_p.board + self.turn_p.traps:
      if card:
        card.effect(f"{timing}_phase_{phase}")
        card.effect(f"{timing}_phase_your_{phase}")
        self.check_field()

    for card in self.other_p.board + self.other_p.traps:
      if card:
        card.effect(f"{timing}_phase_{phase}")
        self.check_field()

    # optional phase effects
    for card in self.turn_p.board + self.turn_p.traps:
      if card:
        card.effect(f"opt_{timing}_phase_{phase}")
        self.check_field()

    for card in self.other_p.board + self.other_p.traps:
      if card:
        card.effect(f"opt_{timing}_phase_{phase}")
        self.check_field()
    self.check_game_over()

  ### CARD ACTIONS ###
  # All of these functions accept a player ["turn", "other"] to bind the
  # effect to (ie., which player did it)

  def play_extradeck(self, ed_idx, player="turn"):
    active = self.get_active_player(player)

    if ed_idx < 0 or ed_idx >= len(active.extradeck):
      raise InvalidMove("Invalid extra deck index")

    card = active.extradeck[ed_idx]

    if not card.can("summon_extradeck"):
      raise InvalidMove("Card cannot activate effect")

    card.effect("summon_extradeck")

    return card

  def play_hand(self, hand_idx, action="", player="turn"):
    active = self.get_active_player(player)

    if hand_idx < 0 or hand_idx >= len(active.hand):
      raise InvalidMove("Invalid hand index")

    card = active.hand[hand_idx]

    if action and not card.can(action):
      raise InvalidMove("Card cannot activate effect")

    if active.can_pay(card.cost):
      active.pay(card.cost)
    else:
      raise InvalidMove("Not enough mana")

    return card

  def summon(self, card, board_idx):
    if board_idx < 0 or board_idx >= len(card.owner.board):
      raise InvalidMove("Invalid board index")

    if card.owner.board[board_idx] is not None:
      raise InvalidMove("Cannot summon; board occupied")

    self.move_to(card, "field", board_idx)

    card.reset_stats()

    # summoning sickness
    card.apply_status(god, "CANNOT_ATTACK", 0, "END")

    card.effect("if_summon_cost")
    card.effect("if_summon")
    act = card.effect("opt_if_summon_cost")
    if act:
      card.effect("opt_if_summon")
    for _, hook in card.owner.hooks["on_owner_summon"]:
      hook(card)
    for _, hook in card.oppon.hooks["on_oppon_summon"]:
      hook(card)

    card.add_hooks()


  def activate_spell(self, card, board_idx):
    if card is None:
      raise InvalidMove("Cannot activate effect; no spell")
    if not card.can("activate_hand"):
      raise InvalidMove("Card cannot activate effect")

    self.move_to(card, "traps", idx=board_idx)

    card.effect("on_activate_hand_cost")
    card.effect("on_activate_hand")

    card.add_hooks()
    if card.type == "spell":
      self.move_to(card, "graveyard")


  def activate_board(self, card):
    if card is None:
      raise InvalidMove("Cannot activate effect; no monster")
    if not card.can("activate"):
      raise InvalidMove("Card cannot activate effect")

    card.effect("on_activate_cost")
    card.effect("on_activate")


  def add_to_hand(self, card):
    self.move_to(card, "hand")

  def banish(self, card):
    self.move_to(card, "banished")

  def bounce(self, card):
    self.move_to(card, "hand")

  def draw(self, player):
    self.move_to(player.deck[-1], "hand")

  def spin(self, card):
    self.move_to(card, "deck")

  def determine_location(self, card):
    if card is None:
      return "unknown"
    locs = ["field", "traps", "hand", "graveyard", "deck", "banished", "extradeck"]
    for loc in locs:
      if card in getattr(card.owner, loc):
        return loc
    return "unknown"

  def remove_card(self, card):
    if card is None:
      return "unknown"
    loc = self.determine_location(card)
    if loc == "field":
      for _, hook in card.oppon.hooks["on_oppon_remove"]:
        hook(card)
      for _, hook in card.owner.hooks["on_owner_remove"]:
        hook(card)
      card.remove_hooks()

      card.effect("on_remove", check_field=False)
      card.owner.board.delete(card)
    elif loc == "traps":
      card.owner.traps.delete(card)

      card.remove_hooks()
    elif loc != "unknown":
      getattr(card.owner, loc).remove(card)

    return loc

  def move_to(self, card, destination, idx=-1):
    if card is None:
      return
    # destination in [hand, field, traps, graveyard, banished, deck]
    from_loc = self.remove_card(card)

    match destination:
      case "hand":
        card.owner.hand.add(card).sort()
        card.reset_stats()

      case "field":
        assert idx >= 0
        card.owner.board[idx] = card
        card.reset_stats()

      case "traps":
        assert idx >= 0
        card.owner.traps[idx] = card
        card.reset_stats()

      case "graveyard":
        card.owner.graveyard.append(card)
        card.reset_stats()

      case "banished":
        card.owner.banished.append(card)
        card.reset_stats()

      case "deck":
        # TODO: move to a specific deck idx without shuffling?
        card.owner.deck.append(card).shuffle()
        card.reset_stats()

      case "extradeck":
        card.owner.deck.append(card).sort()
        card.reset_stats()

    card.owner.io.move_card(card, from_loc, destination, idx)
    card.oppon.io.move_oppon_card(card, from_loc, destination, idx)


  def send_graveyard(self, card):
    return self.send_graveyard_multiple([card])

  def send_graveyard_multiple(self, cards):
    for card in cards:
      if card is None:
        continue
      self.move_to(card, "graveyard")

    for card in cards:
      if card is None:
        continue
      card.effect("if_send_graveyard")
      card.effect("opt_if_send_graveyard")

  def discard(self, card):
    return self.discard_multiple([card])

  def discard_multiple(self, cards):
    for card in cards:
      if card is None:
        continue
      self.move_to(card, "graveyard")

  def destroy(self, card):
    return self.destroy_multiple([card])

  def destroy_multiple(self, cards):
    active = self.get_active_player("turn")
    inactive = self.get_inactive_player("turn")
    cards = [card for card in cards if card is not None]

    if not cards:
      return

    for card in cards:
      card.effect("if_send_graveyard")
    for card in cards:
      for _, hook in card.owner.hooks["on_owner_send_graveyard"]:
        hook(card)
    for card in cards:
      for _, hook in card.oppon.hooks["on_oppon_send_graveyard"]:
        hook(card)
    for card in cards:
      card.effect("opt_if_send_graveyard")

    for card in cards:
      self.move_to(card, "graveyard")

    # destroyed effects
    for card in cards:
      if card.owner == self.turn_p:
        card.effect("if_destroyed")
    for card in cards:
      if card.owner == self.other_p:
        card.effect("if_destroyed")
    for card in cards:
      for _, hook in card.owner.hooks["on_owner_destroyed"]:
        hook(card)
    for card in cards:
      for _, hook in card.oppon.hooks["on_oppon_destroyed"]:
        hook(card)
    for card in cards:
      if card.owner == self.turn_p:
        card.effect("opt_if_destroyed")
    for card in cards:
      if card.owner == self.other_p:
        card.effect("opt_if_destroyed")


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

    inactive.take_damage(attacker, forward)

    attacker.owner.io.display_message(f"Your {attacker.name} attacks directly for {forward}")
    attacker.oppon.io.display_message(f"Their {attacker.name} attacks directly for {forward}")

    attacker.effect("end_attack_directly")
    attacker.effect("opt_end_attack_directly")

    attacker.apply_status(god, "CANNOT_ATTACK", 0, "END")

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

    attackee.take_battle_damage("battle", forward)
    attacker.take_battle_damage("battle", backward)

    attacker.owner.io.display_message(f"Your {attacker.name} attacks their {attackee.name} for {forward}")
    attacker.oppon.io.display_message(f"Their {attacker.name} attacks your {attackee.name} for {forward}")

    # exit damage step
    # TODO

    # check if things are destroyed
    # (do this bc even if a party heals)
    attackee_destroyed = attackee.health <= 0
    attacker_destroyed = attacker.health <= 0

    # send cards to graveyard
    to_gy = []
    if attacker_destroyed:
      to_gy.append(attacker)
    if attackee_destroyed:
      to_gy.append(attackee)
    self.send_graveyard_multiple(to_gy)

    # attacker effects
    if attackee_destroyed:
      attacker.effect("if_destroy_battle", attackee)
    if attacker_destroyed:
      attacker.effect("if_destroyed_battle", attackee)
      attacker.effect("if_destroyed")
      for _, hook in attacker.owner.hooks["on_owner_destroyed"]:
        hook(attacker)
      for _, hook in attacker.oppon.hooks["on_oppon_destroyed"]:
        hook(attacker)
    # attackee effects
    if attacker_destroyed:
      attackee.effect("if_destroy_battle", attacker)
    if attackee_destroyed:
      attackee.effect("if_destroyed_battle", attacker)
      attackee.effect("if_destroyed", attackee)
      for _, hook in attackee.owner.hooks["on_owner_destroyed"]:
        hook(attackee)
      for _, hook in attackee.oppon.hooks["on_oppon_destroyed"]:
        hook(attackee)
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

    attacker.apply_status(god, "CANNOT_ATTACK", 0, "END")

    attacker.effect("end_attack", attackee)
    attackee.effect("end_attacked", attacker)

    attacker.effect("opt_end_attack", attackee)
    attackee.effect("opt_end_attacked", attacker)

    self.check_game_over()



