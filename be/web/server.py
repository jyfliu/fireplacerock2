import socketio
import json
from gevent import pywsgi

import web.room_api as room_api
import web.deck_api as deck_api

sio = socketio.Server(async_mode='gevent', cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

class State:
  def __init__(self):

    self.sid_to_name = {}
    self.name_to_sid = {}

    self.challenge_map = {}

    self.room_id = 0
    self.rooms = {}
    self.room_map = {}

    with open("database/accounts.json", "r") as f:
      self.accounts = json.load(f)

  def login(self, username, password):
    if username in self.accounts:
      if password == self.accounts[username]["password"]:
        state = "success"
      else:
        state = "wrong_password"
    else:
      state = "wrong_username"

    return state

  def new_user(self, username, password):
    if username in self.accounts or not password:
      return False
    self.accounts[username] = {
      "password": password,
    }
    with open("database/accounts.json", "w") as f:
      json.dump(self.accounts, f, indent=4)
    return True

  def record_game_result(self, name, result):
    with open("database/elo.json", "r") as f:
      record = json.load(f)
    if name not in record:
      record[name] = {
        "win": 0,
        "loss": 0,
        "draw": 0,
      }
    match result:
      case -1:
        record[name]["loss"] += 1
      case 0:
        record[name]["draw"] += 1
      case 1:
        record[name]["win"] += 1
    with open("database/elo.json", "w") as f:
      json.dump(record, f, indent=4)

state = State()

# input

@sio.event
def connect(sid, environ):
  print(f"[EVENT-{sid}] connect")

@sio.event
def login(sid, username, password):
  result = state.login(username, password)
  if result == "success":
    state.sid_to_name[sid] = username
    state.name_to_sid[username] = sid
  print(f"[EVENT-{sid}] login {username} {result}")

  return result

@sio.event
def new_user(sid, username, password):
  success = state.new_user(username, password)
  print(f"[EVENT-{sid}] new_user {username} {success}")

  return success


@sio.event
def challenge(sid, challengee):
  challenger = state.sid_to_name[sid]
  name = state.sid_to_name[sid]
  print(f"[EVENT-{sid}] challenge: {challenger} -> {challengee}")
  if challengee in state.challenge_map and state.challenge_map[challengee] == challenger:
    # if there was already an existing challenge
    # create new room (TODO move to own thread)
    room_id = state.room_id
    room = room_api.Room(None, challengee, challenger)
    state.rooms[room_id] = room
    state.room_map[challengee] = room_id
    state.room_map[challenger] = room_id
    state.room_id += 1

    # start duel
    # room.start_duel((deck_api.sd_cs, deck_api.ed_cs), (deck_api.sd_sv, deck_api.ed_sv))
    room.start_duel((deck_api.deck1, deck_api.ed_pote), (deck_api.deck2, deck_api.ed_cs))
  else:
    state.challenge_map[challenger] = challengee
    if challengee in state.name_to_sid:
      sio.emit("challenged", challenger, room=state.name_to_sid[challengee])

@sio.event
def player_action(sid, action):
  name = state.sid_to_name[sid]
  print(f"[EVENT-{sid}] player {name} action {action}")
  actor = state.sid_to_name[sid]
  room_id = state.room_map[actor]
  room = state.rooms[room_id]

  room.player_action(actor, action)

@sio.event
def card_can(sid, card_uuid, action):
  actor = state.sid_to_name[sid]
  room_id = state.room_map[actor]
  room = state.rooms[room_id]

  room.card_can(actor, card_uuid, action)

@sio.event
def disconnect(sid):
  username = state.sid_to_name[sid]
  print(f"[EVENT-{sid}] player {username} disconnect")
  del state.sid_to_name[sid]
  del state.name_to_sid[username]

# output
def emit(*args, sid):
  name = state.sid_to_name[sid]
  args_str = [str(arg) for arg in args]
  args_str = [a[:30] + "..." + a[-30:] if len(a) > 60 else a for a in args_str]
  args_str = ", ".join(args_str)
  print(f"[EMIT-{sid}] player {name} emit ({args_str})")
  sio.emit(*args, room=sid)

def call(*args, sid):
  name = state.sid_to_name[sid]
  args_str = [str(arg) for arg in args]
  args_str = [a[:30] + "..." + a[-30:] if len(a) > 60 else a for a in args_str]
  args_str = ", ".join(args_str)
  print(f"[CALL-{sid}] player {name} call ({args_str})")
  response = sio.call(*args, sid=sid, timeout=9999)
  print(f"[CALL-{sid}] player {name} {args[0]} response {response}")
  return response

# init
def run():
  pywsgi.WSGIServer(("", 8443), app, certfile="/home/jeffr/.ssl/server.cert", keyfile="/home/jeffr/.ssl/server.key").serve_forever()

