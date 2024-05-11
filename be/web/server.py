import socketio
import eventlet

import web.room_api as room_api
import web.deck_api as deck_api

sio = socketio.Server(async_mode='eventlet', cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

class State:
  def __init__(self):

    self.sid_to_name = {}
    self.name_to_sid = {}

    self.challenge_map = {}

    self.room_id = 0
    self.rooms = {}
    self.room_map = {}

state = State()

@sio.event
def connect(sid, environ):
  print(f"[EVENT-{sid}] connect")

@sio.event
def login(sid, username):
  state.sid_to_name[sid] = username
  state.name_to_sid[username] = sid
  print(f"[EVENT-{sid}] login {username}")

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
    room.start_duel((deck_api.sd_pote, deck_api.ed_pote), (deck_api.sd_cs, deck_api.ed_cs))
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
  print(f"[EVENT-{sid}] disconnect")
  username = state.sid_to_name[sid]
  del state.sid_to_name[sid]
  del state.name_to_sid[username]

def run():
  eventlet.wsgi.server(eventlet.listen(("", 9069)), app)

