// functions that call server functions and wait for response


export function EmitNextPhase(socket) {
  return () => {
    console.log("player_action [pass]");
    socket.emit("player_action", ["pass"]);
  }
};


export function EmitNextTurn(socket) {
  return () => {
    for (let i = 0; i < 6; ++i) {
      console.log("player_action [pass]");
      socket.emit("player_action", ["pass"]);
    }
  }
};

export function Summon(socket) {
  return (handIdx, boardIdx) => {
    console.log("summon", handIdx, boardIdx);
    socket.emit("player_action", ["summon", handIdx, boardIdx]);
  }
}

export function ActivateSpell(socket) {
  return (handIdx, boardIdx) => {
    console.log("activate_spell", handIdx, boardIdx);
    socket.emit("player_action", ["activate_spell", handIdx, boardIdx]);
  }
}

export function Attack(socket) {
  return (attackerIdx, attackeeIdx) => {
    console.log("attack", attackerIdx, attackeeIdx);
    socket.emit("player_action", ["attack", attackerIdx, attackeeIdx]);
  }
}

export function AttackDirectly(socket) {
  return (attackerIdx) => {
    console.log("attack_directly", attackerIdx);
    socket.emit("player_action", ["attack_directly", attackerIdx]);
  }
}

export function ActivateBoard(socket, states) {
  const { field } = states;
  return (boardIdx) => {
    if (!field.ownerMonsters[boardIdx]) { return; }
    const { name } = field.ownerMonsters[boardIdx];
    let response = window.confirm(`Activate ${name}'s effect?'`);
    if (response) {
      console.log("activate_board", boardIdx);
      socket.emit("player_action", ["activate_board", boardIdx]);
    }
  }
}

export function ActivateFieldSpell(socket, states) {
  const { field } = states;
  return (fieldIdx) => {
    if (!field.ownerTraps[fieldIdx]) { return; }
    const { name } = field.ownerTraps[fieldIdx];
    let response = window.confirm(`Activate ${name}'s effect?'`);
    if (response) {
      console.log("activate_field_spell", fieldIdx);
      socket.emit("player_action", ["activate_field_spell", fieldIdx]);
    }
  }
}

//export function callCardCan(socket, states, card_uuid, action) {
  //let { setCardCan } = states;
  //let ack = (yesno) => {
    //setCardCan(cardCan => yesno);
  //}

  //socket.call("card_can", card_uuid, action, ack);
//};



