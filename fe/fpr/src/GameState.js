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


export function OnMoveCard(states) {
  let { setOwnerHand } = states;
  return (card, from, to, idx) => {
    // remove
    switch (from) {
      case "hand":
        break;
      case "field":
        break;
      case "graveyard":
        break;
      case "banished":
        break;
      case "deck":
        break;
      case "extradeck":
        break;
      default:
        break;
    };
    // add
    switch (to) {
      case "hand":
        card.id = card.uuid;
        card.parent = null;
        setOwnerHand(ownerHand => {
          ownerHand = [...ownerHand]
          ownerHand.push(card);
          ownerHand.sort((a, b) => {
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
          });
          return ownerHand;
        });
        break;
      case "field":
        break;
      case "graveyard":
        break;
      case "banished":
        break;
      case "deck":
        break;
      case "extradeck":
        break;
      default:
        break;
    }
  };

}

export function OnMoveOpponCard(states) {
  let { setOpponHand } = states;
  return (card, from, to, idx) => {
    // remove
    switch (from) {
      case "hand":
        break;
      case "field":
        break;
      case "graveyard":
        break;
      case "banished":
        break;
      case "deck":
        break;
      case "extradeck":
        break;
      default:
        break;
    };
    // add
    switch (to) {
      case "hand":
        setOpponHand(opponHand => opponHand + 1);
        break;
      case "field":
        break;
      case "graveyard":
        break;
      case "banished":
        break;
      case "deck":
        break;
      case "extradeck":
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

export function OnGameOver(states) {
  return (winner) => {
    alert(winner);
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
