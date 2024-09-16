import multiprocessing as mp
import socketio
import yaml
from easydict import EasyDict as edict

import gameplay.callbacks
import gameplay.duel_api as duel_api
import gameplay.card_api as card_api
import web.api_utils as api_utils
from . import server as se

class Collection:
        
    def init_collection(self, sid):
        with open("../res/cards/fireplacerock.yaml", "r", encoding="utf8") as f:
            cards = yaml.safe_load(f)
            cards = edict(cards)

        cards = cards.values()
        
        with mp.Pool(1) as p:
            cards = p.map(card_api.Template, cards)

        all_cards = [api_utils.serialize_template(card) for card in cards]
        return all_cards