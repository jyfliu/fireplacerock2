// functions that change the game state based on server call


function UnserializeCard(states) {
  let { setCardCache } = states;
  const unserializeCard = (card) => {
    if (!card) {
      return card;
    }
    card.id = card.uuid;
    card.parent = null;
    card.isSelected = false;

    if (card.sprite) {
      let sprite_img = new Image();
      sprite_img.src = `data:image/jpg;base64,${card.sprite}`;

      setCardCache(cache => ({...cache, [card.template_id]: {image: sprite_img, isMini: false}}));
    }

    if (card.mini_sprite) {
      let sprite_img = new Image();
      sprite_img.src = `data:image/jpg;base64,${card.mini_sprite}`;

      setCardCache(cache => ({...cache, [card.template_id]: {image: sprite_img, isMini: true}}));
    }

    return card;
  };
  return unserializeCard;
}

export function OnInitGameState(states) {
  let {
    setOwnerStats,
    setOpponStats,
    setOwnerHand,
    setOwnerCards,
    setOpponHand,
    setOpponCards,
    setField,
    pushChat,
  } = states;
  let unserializeCard = UnserializeCard(states);
  return (
    owner,
    oppon,
    ownerHand,
    ownerMonsters,
    ownerGraveyard,
    ownerBanished,
    ownerMainDeck,
    ownerExtraDeck,
    opponHand,
    opponMonsters,
    opponGraveyard,
    opponBanished,
    opponMainDeck,
    opponExtraDeck,
  ) => {
    pushChat("[dbg] loaded game state");
    setOwnerStats(stats => ({
      hp: owner.life,
      mana: owner.mana,
      manaMax: owner.mana_max,
    }));
    setOpponStats(stats => ({
      hp: oppon.life,
      mana: oppon.mana,
      manaMax: oppon.mana_max,
    }));
    setOwnerHand(ownerHand.map(unserializeCard).toSorted(cardSortKey));
    setOpponHand(opponHand);
    setOwnerCards(cards => ({
      ownerGraveyard: ownerGraveyard.map(unserializeCard),
      ownerBanished: ownerBanished.map(unserializeCard),
      ownerMainDeck: ownerMainDeck,
      ownerExtraDeck: ownerExtraDeck.map(unserializeCard),
    }));
    setOpponCards(cards => ({
      opponGraveyard: opponGraveyard.map(unserializeCard),
      opponBanished: opponBanished.map(unserializeCard),
      opponMainDeck: opponMainDeck,
      opponExtraDeck: opponExtraDeck,
    }));
    setField(field => ({
      ...field,
      ownerMonsters: ownerMonsters.map(unserializeCard),
      opponMonsters: opponMonsters.map(unserializeCard),
    }));
  };
}

export function OnPromptUserActivate(states) {
  let { pushChat } = states;
  return (name, cb) => {
    let response = window.confirm(`Activate ${name}'s effect?'`);
    let responseStr = response? "Activated" : "Did not activate";
    pushChat(`${responseStr} ${name}'s effect`);
    cb(response);
  };
};

export function OnPromptUserSelectCards(states) {
  let { pushChat, setModalVisible, setModalState } = states;
  let unserializeCard = UnserializeCard(states);
  return (locAndCards, amount, cb) => {
    let selected = [];
    let highlightIds = [];
    let cards = locAndCards.map(locAndCard => locAndCard[1]).map(unserializeCard);
    setModalState(modal => ({
      title: "Select a card",
      cards: cards,
      onClickCard: (card) => {
        let response = cards.map(c => c.id).indexOf(card.id);
        let loc = locAndCards[response][0];
        if (!selected.includes(response)) {
          pushChat(`Selected ${card.name} from ${loc}`);
          selected.push(response);
          highlightIds.push(card.id);
        } else {
          pushChat(`Unselected ${card.name} from ${loc}`);
          selected = selected.filter(x => x !== response);
          highlightIds = highlightIds.filter(x => x !== card.id);
        }
        setModalState(m => ({...m, highlightIds: highlightIds}));
      },
      onClickOK: () => {
        if (amount.includes(selected.length)) {
          cb(selected);
          setModalVisible(false);
        } else {
          alert("Incorrect number of cards selected");
        }
      }
    }));
    setModalVisible(true);
  };
};

export function OnPromptUserSelectText(states) {
  let { pushChat } = states;
  return (options, cb) => {
    let optStr = options.map((txt, idx) => `[${idx}: ${txt}]`).join(" ");
    do {
      let response = prompt(`Select an option ${optStr}`);
      if (options[response] !== undefined) {
        pushChat(`Selected ${options[response]}`);
        cb(response);
        break;
      }
    } while (true);
  }
}

export function OnPromptUserSelectBoard(states) {
  let { pushChat } = states;
  return (nums, cb) => {
    do {
      let response = prompt(`Select a board position [${nums}]`);
      if (nums.includes(parseInt(response))) {
        pushChat(`Selected board position ${response}`);
        cb(response);
        break;
      }
    } while (true);
  }
}

export function OnTakeDamage(states) {
  let { pushChat, setOwnerStats } = states;
  return (amount) => {
    pushChat(`You took ${amount} damage`);
    setOwnerStats(old => {
      let stats = {...old};
      stats.hp -= amount;
      return stats;
    });
  }
}

export function OnOpponTakeDamage(states) {
  let { pushChat, setOpponStats } = states;
  return (amount) => {
    pushChat(`Your opponent took ${amount} damage`);
    setOpponStats(old => {
      let stats = {...old};
      stats.hp -= amount;
      return stats;
    });
  }
}

export function OnPayMana(states) {
  let { pushChat, setOwnerStats } = states;
  return (amount) => {
    pushChat(`You paid ${amount} mana`);
    setOwnerStats(old => {
      let stats = {...old};
      stats.mana -= amount;
      return stats;
    })
  }
}

export function OnOpponPayMana(states) {
  let { pushChat, setOpponStats } = states;
  return (amount) => {
    pushChat(`Your opponent paid ${amount} mana`);
    setOpponStats(old => {
      let stats = {...old};
      stats.mana -= amount;
      return stats;
    })
  }
}

export function OnRestoreMana(states) {
  let { pushChat, setOwnerStats } = states;
  return (mana, manaMax) => {
    pushChat(`Your mana was restored to ${mana}`);
    setOwnerStats(old => {
      let stats = {...old};
      stats.mana = mana;
      stats.manaMax = manaMax;
      return stats;
    })
  }
}

export function OnOpponRestoreMana(states) {
  let { pushChat, setOpponStats } = states;
  return (mana, manaMax) => {
    pushChat(`Your opponent's mana was restored to ${mana}`);
    setOpponStats(old => {
      let stats = {...old};
      stats.mana = mana;
      stats.manaMax = manaMax;
      return stats;
    })
  }
}

let cardSortKey = (a, b) => {
  if (a["type"] === b["type"]) {
    if (a["cost"] === b["cost"]) {
      if (a["name"] === b["name"]) {
        return a["uuid"] - b["uuid"];
      } else {
        return a["name"] < b["name"] ? -1 : 1;
      }
    } else {
      return a["cost"] - b["cost"];
    }
  } else {
    return a["type"] < b["type"] ? -1 : 1;
  }
};

export function OnMoveCard(states) {
  let { pushChat, setOwnerHand, setField, setOwnerCards } = states;
  let unserializeCard = UnserializeCard(states);
  return (card, from, to, idx) => {
    pushChat(`Your ${card?.name} was sent from your ${from} to your ${to}`);
    let shouldKeep = c => c? c.uuid !== card.uuid : true;
    let keepOthers = c => shouldKeep(c)? c : null;
    // remove
    switch (from) {
      case "hand":
        setOwnerHand(ownerHand => ownerHand.filter(shouldKeep));
        break;
      case "field":
        setField(field => ({
          ...field,
          ownerMonsters: field.ownerMonsters.map(keepOthers),
        }));
        break;
      case "traps":
        setField(field => ({
          ...field,
          ownerTraps: field.ownerTraps.map(keepOthers),
        }));
        break;
      case "graveyard":
        setOwnerCards(cards => ({
          ...cards,
          ownerGraveyard: cards.ownerGraveyard.filter(shouldKeep),
        }));
        break;
      case "banished":
        setOwnerCards(cards => ({
          ...cards,
          ownerBanished: cards.ownerBanished.filter(shouldKeep),
        }));
        break;
      case "deck":
        setOwnerCards(cards => ({
          ...cards,
          ownerMainDeck: cards.ownerMainDeck - 1,
        }));
        break;
      case "extradeck":
        setOwnerCards(cards => ({
          ...cards,
          ownerExtraDeck: cards.ownerExtraDeck.filter(shouldKeep),
        }));
        break;
      default:
        break;
    };
    let copyAndAppend = list => {
      list = [...list];
      list.push(card);
      return list;
    };
    card = unserializeCard(card);
    // add
    switch (to) {
      case "hand":
        setOwnerHand(ownerHand => copyAndAppend(ownerHand).toSorted(cardSortKey))
        break;
      case "field":
        setField(field => {
          let ownerMonsters = [...field.ownerMonsters];
          card.parent = idx + 10;
          ownerMonsters[idx] = card;
          return ({
            ...field,
            ownerMonsters: ownerMonsters,
          });
        });
        break;
      case "traps":
        setField(field => {
          let ownerTraps = [...field.ownerTraps];
          card.parent = idx + 15;
          ownerTraps[idx] = card;
          return ({
            ...field,
            ownerTraps: ownerTraps,
          });
        });
        break;
      case "graveyard":
        setOwnerCards(cards => ({
          ...cards,
          ownerGraveyard: copyAndAppend(cards.ownerGraveyard),
        }));
        break;
      case "banished":
        setOwnerCards(cards => ({
          ...cards,
          ownerBanished: copyAndAppend(cards.ownerBanished),
        }));
        break;
      case "deck":
        setOwnerCards(cards => ({
          ...cards,
          ownerMainDeck: cards.ownerMainDeck + 1,
        }));
        break;
      case "extradeck":
        setOwnerCards(cards => ({
          ...cards,
          ownerExtraDeck: copyAndAppend(cards.ownerExtraDeck).toSorted(cardSortKey),
        }));
        break;
      default:
        break;
    }
  };

}

export function OnMoveOpponCard(states) {
  let { pushChat, setOpponHand, setField, setOpponCards } = states;
  let unserializeCard = UnserializeCard(states);
  return (card, from, to, idx) => {
    // should be moved server side
    let isVisible = loc => ["field", "graveyard", "banished"].includes(loc);
    let maybeCardName = isVisible(from) || isVisible(to)? card?.name : "card";

    pushChat(`Your opponent's ${maybeCardName} was sent from their ${from} to their ${to}`);
    let shouldKeep = c => c? c.uuid !== card.uuid : true;
    let keepOthers = c => shouldKeep(c)? c : null;

    card = unserializeCard(card);
    // remove
    switch (from) {
      case "hand":
        setOpponHand(opponHand => opponHand - 1);
        break;
      case "field":
        setField(field => ({
          ...field,
          opponMonsters: field.opponMonsters.map(keepOthers),
        }));
        break;
      case "graveyard":
        setOpponCards(cards => ({
          ...cards,
          opponGraveyard: cards.opponGraveyard.filter(shouldKeep),
        }));
        break;
      case "banished":
        setOpponCards(cards => ({
          ...cards,
          opponBanished: cards.opponBanished.filter(shouldKeep),
        }));
        break;
      case "deck":
        setOpponCards(cards => ({
          ...cards,
          opponMainDeck: cards.opponMainDeck - 1,
        }));
        break;
      case "extradeck":
        setOpponCards(cards => ({
          ...cards,
          opponExtraDeck: cards.opponExtraDeck - 1,
        }));
        break;
      default:
        break;
    };
    let copyAndAppend = list => {
      list = [...list];
      list.push(card);
      return list;
    };
    // add
    switch (to) {
      case "hand":
        setOpponHand(opponHand => opponHand + 1);
        break;
      case "field":
        setField(field => {
          let opponMonsters = [...field.opponMonsters];
          opponMonsters[idx] = card;
          return ({
            ...field,
            opponMonsters: opponMonsters,
          });
        });
        break;
      case "graveyard":
        setOpponCards(cards => ({
          ...cards,
          opponGraveyard: copyAndAppend(cards.opponGraveyard),
        }));
        break;
      case "banished":
        setOpponCards(cards => ({
          ...cards,
          opponBanished: copyAndAppend(cards.opponBanished),
        }));
        break;
      case "deck":
        setOpponCards(cards => ({
          ...cards,
          opponMainDeck: cards.opponMainDeck - 1,
        }));
        break;
      case "extradeck":
        setOpponCards(cards => ({
          ...cards,
          opponExtraDeck: cards.opponExtraDeck - 1,
        }));
        break;
      default:
        break;
    }
  };

}

export function OnFlipCoin(states) {
  let { pushChat } = states;
  return (result) => {
    let res = result? "Heads" : "Tails";
    pushChat(`Flipped a coin: ${res}!`);
  }
}

export function OnDisplayMessage(states) {
  let { pushChat } = states;
  return (message) => {
    pushChat(message);
  }
}

export function OnGameStart(states) {
  const {
    pushChat,
    setPhase,
    setHasInitiative,
    setOwnerHand,
    setOpponHand,
    setOwnerStats,
    setOpponStats,
  } = states;
  return () => {
    pushChat("Game started!");
    setPhase(x => ["owner", "draw"]);
    setHasInitiative(x => false);
    setOwnerHand(x => []);
    setOpponHand(x => 0);
    setOwnerStats(x => ({
      hp: 0,
      mana: 0,
      manaMax: 0,
    }));
    setOpponStats(x => ({
      hp: 0,
      mana: 0,
      manaMax: 0,
    }));
  }
}

export function OnGameOver(states) {
  return (winner) => {
    if (winner === 1) {
      alert("You win! :D")
    } else if (winner === -1) {
      alert("You lose. :(")
    } else {
      alert("You draw. :|")
    }
  }
}

export function OnBeginPhase(states) {
  let { pushChat, setPhase, setHasInitiative } = states;
  return (player, phase) => {
    let phaseText = player === "owner"? "Your" : "Your opponent's";
    pushChat(`${phaseText} ${phase} phase`);
    setPhase(x => [player, phase]);
    setHasInitiative(x => true);
  }
}

export function OnEndTurn(states) {
  let { pushChat, setHasInitiative } = states;
  return () => {
    pushChat(`Your opponent's turn starts`);
    setHasInitiative(x => false);
  }
}

export function DrawPhasePrompt(states) {
  let { setPhase } = states;
  return () => {
    setPhase(phase => ["owner", "draw"]);
  }
}

export function MainPhasePrompt(states) {
  let { setPhase } = states;
  return (main_phase_2) => {
    setPhase(phase => ["owner", "draw"]);
  }
}


function allCardsMap(states, lambda) {
  let { setOwnerHand, setField, setOwnerCards, setOpponCards } = states;
  let lambdaIfNotNull = card => card? lambda(card) : card;
  setOwnerHand(hand => hand.map(lambdaIfNotNull));
  setField(field =>
    ({
      opponTraps: field.opponTraps.map(lambdaIfNotNull),
      opponMonsters: field.opponMonsters.map(lambdaIfNotNull),
      ownerMonsters: field.ownerMonsters.map(lambdaIfNotNull),
      ownerTraps: field.ownerTraps.map(lambdaIfNotNull),
    })
  );
  setOwnerCards(cards =>
    ({
      ...cards,
      ownerGraveyard: cards.ownerGraveyard.map(lambdaIfNotNull),
      ownerBanished: cards.ownerBanished.map(lambdaIfNotNull),
      ownerExtraDeck: cards.ownerExtraDeck.map(lambdaIfNotNull),
    })
  );
  setOpponCards(cards =>
    ({
      ...cards,
      opponGraveyard: cards.opponGraveyard.map(lambdaIfNotNull),
      opponBanished: cards.opponBanished.map(lambdaIfNotNull),
    })
  );
}

export function OnCardChangeName(states) {
  let { pushChat } = states;
  return (uuid, newName) => allCardsMap(states,
    (card) => {
      if (card.uuid === uuid) {
        pushChat(`${card.name}'s name was changed to ${newName}`);
        return {...card, name: newName};
      } else {
        return card;
      }
    }
  );
}

export function OnCardGain(states) {
  let { pushChat } = states;
  return (uuid, source, attack, health) => allCardsMap(states,
    (card) => {
      if (card.uuid === uuid) {
        pushChat(`${card.name} gained ${attack} / ${health}`);
        return {...card, attack: card.attack + attack, health: card.health + health};
      } else {
        return card;
      }
    }
  );
}

export function OnCardLose(states) {
  let { pushChat } = states;
  return (uuid, source, attack, health) => allCardsMap(states,
    (card) => {
      if (card.uuid === uuid) {
        pushChat(`${card.name} lost ${attack} / ${health}`);
        return {...card, attack: card.attack - attack, health: card.health - health};
      } else {
        return card;
      }
    }
  );
}

export function OnCardTakeDamage(states) {
  let { pushChat } = states;
  return (uuid, source, amount) => allCardsMap(states,
    (card) => {
      if (card.uuid === uuid) {
        pushChat(`${card.name} took ${amount} damage`);
        return {...card, health: card.health - amount};
      } else {
        return card;
      }
    }
  );
}

export function OnCardSet(states) {
  let { pushChat } = states;
  return (uuid, source, attack, health) => allCardsMap(states,
    (card) => {
      if (card.uuid === uuid) {
        if (card.attack !== attack || card.health !== health) {
          pushChat(`${card.name} changed from ${card.attack} / ${card.health} to ${attack} / ${health}`);
        }
        return {...card, attack: attack, health: health};
      } else {
        return card;
      }
    }
  );
}


