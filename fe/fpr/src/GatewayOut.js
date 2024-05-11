// functions that call server functions and wait for response


export function EmitNextPhase(socket) {
  return () => {
    console.log("player_action [pass]");
    socket.emit("player_action", ["pass"]);
  }
};

export function Summon(socket) {
  return (handIdx, boardIdx) => {
    console.log("summon", handIdx, boardIdx);
    socket.emit("player_action", ["summon", handIdx, boardIdx]);
  }
}



//export function callCardCan(socket, states, card_uuid, action) {
  //let { setCardCan } = states;
  //let ack = (yesno) => {
    //setCardCan(cardCan => yesno);
  //}

  //socket.call("card_can", card_uuid, action, ack);
//};



