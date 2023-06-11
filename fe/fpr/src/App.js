import React, { useState, useEffect } from 'react';
import { DndContext } from '@dnd-kit/core';

import { socket } from './socket';

import { BoardSpace } from './components/BoardSpace';
import { Card } from './components/Card';
import { PlayerStats, PlayerMana } from './components/PlayerStats';

import { OnMoveCard, OnMoveOpponCard } from "./GameState"

import './App.css';

function App() {
  const [isConnected, setIsConnected] = useState(false);

  const [phase, setPhase] = useState(["owner", "draw"]);
  const [ownerHand, setOwnerHand] = useState([]);
  const [opponHand, setOpponHand] = useState(0)

  useEffect(() => {
    let onConnect = () => {
      setIsConnected(true);

      let name = prompt("[WIP] What is your name?");
      let oppo = prompt("Who would you like to challenge?");
      socket.emit("login", name)
      socket.emit("challenge", oppo)
    };
    let onDisconnect = () => {
      setIsConnected(false);
    };

    let setStates = {
      setOwnerHand: setOwnerHand,
      setOpponHand: setOpponHand,
      setPhase: setPhase,
    };

    let onMoveCard = OnMoveCard(setStates);
    let onMoveOpponCard = OnMoveOpponCard(setStates);

    socket.on("connect", onConnect);
    socket.on("disconnect", onDisconnect);
    socket.on("move_card", onMoveCard);
    socket.on("move_oppon_card", onMoveOpponCard);

    return () => {
      socket.off("connect", onConnect);
      socket.off("disconnect", onDisconnect);
      socket.off("move_card", onMoveCard);
      socket.off("move_oppon_card", onMoveOpponCard);
    };
  }, []);


  const containers = [
    0, 1, 2, 3, 4,
    5, 6, 7, 8, 9,
    10, 11, 12, 13, 14,
    15, 16, 17, 18, 19
  ];

  const displayCard = card =>
    <Card id={card.id} key={card.id} card={card} inDroppable={card.parent===null} />


  const statusStyle = {
    "color": isConnected? "green" : "red"
  }

  return (
    <DndContext onDragEnd={handleDragEnd}>
      <p style={statusStyle} class="status-bar">
        {isConnected ? "Connected: ip=0.0.0.0:9069" : "Disconnected"}
      </p>
      <div class="battle">
        <div class="oppon-hand">
          {
            Array.from(Array(opponHand).keys()).map(id => ({
              id: id,
              name: "",
              parent: null,
            })).map(displayCard)
          }
        </div>
        <PlayerStats owner={true} hp={3000} />
        <PlayerStats owner={false} hp={3000} />
        <PlayerMana owner={true} mana={5} manaMax={8} />
        <PlayerMana owner={false} mana={1} manaMax={8} />
        <div class="phase-indicator">
          <button>{phase[0] === "owner"? "Your" : "Your opponent's"}<br />{phase[1]} phase</button>
        </div>
        <div class="phase-select">
          <button>Next Phase</button>
          <button class="end-button">End Turn</button>
        </div>
        <div class="board-grid">
          {containers.map((id) => (
            // We updated the Droppable component so it would accept an `id`
            // prop and pass it to `useDroppable`
            <div class="card-griditem">
              <BoardSpace key={id} id={id}>
                {ownerHand.filter(card => card.parent === id).map(displayCard)}
              </BoardSpace>
            </div>
          ))}
        </div>
        <div class="owner-hand">
          {ownerHand.filter(card => card.parent === null).map(displayCard)}
        </div>
      </div>
    </DndContext>
  );

  function handleDragEnd(event) {
    const { active, over } = event;

    // If the item is dropped over a container, set it as the parent
    // otherwise reset the parent to `null`
    setOwnerHand(ownerHand.map(
      card =>
        card.id === active.id?
        {...card, parent: over? over.id : null}
        : card
    ))
  }
};

export default App;
