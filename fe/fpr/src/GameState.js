export function PromptUserActivate(states) {
  return name => window.confirm(`Activate ${name}'s effect?'`);
};

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
