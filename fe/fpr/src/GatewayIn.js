// functions that change the game state based on server call

export function OnPromptUserActivate(states) {
  return name => window.confirm(`Activate ${name}'s effect?'`);
};

export function OnPromptUserSelect(states) {
  return cards => prompt(`Select a card ${cards.length}`);
};

export function OnPromptUserSelectMultiple(states) {
  return (cards, amounts) => prompt(`Select a card ${cards.length}`);
}

export function OnPromptUserSelectText(states) {
  return options => prompt(`Select an option ${options.length}`);
}

export function OnPromptUserSelectBoard(states) {
  return nums => prompt(`Select an option ${nums.length}`);
}

export function OnTakeDamage(states) {
  let { setOwnerStats } = states;
  return (amount) => {
    setOwnerStats(old => {
      let stats = {...old};
      stats.lp -= amount;
      return stats;
    })
  }
}

export function OnOpponTakeDamage(states) {
  let { setOpponStats } = states;
  return (amount) => {
    setOpponStats(old => {
      let stats = {...old};
      stats.lp -= amount;
      return stats;
    })
  }
}

export function OnPayMana(states) {
  let { setOwnerStats } = states;
  return (amount) => {
    setOwnerStats(old => {
      let stats = {...old};
      stats.mana -= amount;
      return stats;
    })
  }
}

export function OnOpponPayMana(states) {
  let { setOpponStats } = states;
  return (amount) => {
    setOpponStats(old => {
      let stats = {...old};
      stats.mana -= amount;
      return stats;
    })
  }
}

export function OnRestoreMana(states) {
  let { setOwnerStats } = states;
  return (mana, manaMax) => {
    setOwnerStats(old => {
      let stats = {...old};
      stats.mana = mana;
      stats.manaMax = manaMax;
      return stats;
    })
  }
}

export function OnOpponRestoreMana(states) {
  let { setOpponStats } = states;
  return (mana, manaMax) => {
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
  let { setOwnerHand, setField, setOwnerCards } = states;
  return (card, from, to, idx) => {
    let shouldKeep = c => c.uuid !== card.uuid;
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
    // add
    switch (to) {
      case "hand":
        card.id = card.uuid;
        card.parent = null;
        card.isSelected = false;
        setOwnerHand(ownerHand => copyAndAppend(ownerHand).toSorted(cardSortKey))
        break;
      case "field":
        setField(field => {
          let ownerMonsters = [...field.ownerMonsters];
          ownerMonsters[idx] = card;
          return ({
            ...field,
            ownerMonsters: ownerMonsters,
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
  let { setOpponHand, setField, setOpponCards } = states;
  return (card, from, to, idx) => {
    let shouldKeep = c => c.uuid !== card.uuid;
    let keepOthers = c => shouldKeep(c)? c : null;
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
  return (result) => {
    let res = result? "Heads" : "Tails";
    alert(`Flipped a coin: ${res}!`);
  }
}

export function OnDisplayMessage(states) {
  return (message) => {
    alert(message);
  }
}

export function OnGameStart(states) {
  const {
    setPhase,
    setHasInitiative,
    setOwnerHand,
    setOpponHand,
    setOwnerStats,
    setOpponStats,
  } = states;
  return () => {
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
    alert(winner);
  }
}

export function OnBeginPhase(states) {
  let { setPhase, setHasInitiative } = states;
  return (player, phase) => {
    setPhase(x => [player, phase]);
    setHasInitiative(x => true);
  }
}

export function OnEndTurn(states) {
  let { setHasInitiative } = states;
  return () => {
    setHasInitiative(x => false);
  }
}

export function DrawPhasePrompt(states) {
  let { setPhase } = states;
  return () => setPhase(phase => ["owner", "draw"]);
}

export function MainPhasePrompt(states) {
  let { setPhase } = states;
  return (main_phase_2) => {
    setPhase(phase => ["owner", "draw"]);
  }
}

