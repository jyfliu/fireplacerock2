import React, { useState, useEffect } from 'react';
import { DndContext } from '@dnd-kit/core';

import { socket } from './socket';

import { BoardSpace } from './components/BoardSpace';
import { Card } from './components/Card';
import { PlayerStats, PlayerMana } from './components/PlayerStats';

import {
  OnPromptUserActivate, OnPromptUserSelect, OnPromptUserSelectMultiple,
  OnPromptUserSelectText, OnPromptUserSelectBoard,
  OnTakeDamage, OnOpponTakeDamage, OnPayMana, OnOpponPayMana,
  OnRestoreMana, OnOpponRestoreMana, OnMoveCard, OnMoveOpponCard,
  OnFlipCoin, OnDisplayMessage, OnGameOver,
} from "./GameState"

import './App.css';

function App() {
  const [isConnected, setIsConnected] = useState(false);

  const [phase, setPhase] = useState(["owner", "draw"]);
  const [ownerHand, setOwnerHand] = useState([]);
  const [opponHand, setOpponHand] = useState(0);
  const [ownerStats, setOwnerStats] = useState({
    hp: 0,
    mana: 0,
    manaMax: 0,
  });
  const [opponStats, setOpponStats] = useState({
    hp: 0,
    mana: 0,
    manaMax: 0,
  });

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
      setOwnerStats: setOwnerStats,
      setOpponStats: setOpponStats,
    };

    // query user input
    let onPromptUserActivate = OnPromptUserActivate(setStates);
    let onPromptUserSelect = OnPromptUserSelect(setStates);
    let onPromptUserSelectMultiple = OnPromptUserSelectMultiple(setStates);
    let onPromptUserSelectText = OnPromptUserSelectText(setStates);
    let onPromptUserSelectBoard = OnPromptUserSelectBoard(setStates);

    // update state functions
    let onTakeDamage = OnTakeDamage(setStates);
    let onOpponTakeDamage = OnOpponTakeDamage(setStates);
    let onPayMana = OnPayMana(setStates);
    let onOpponPayMana = OnOpponPayMana(setStates);
    let onRestoreMana = OnRestoreMana(setStates);
    let onOpponRestoreMana = OnOpponRestoreMana(setStates);

    let onMoveCard = OnMoveCard(setStates);
    let onMoveOpponCard = OnMoveOpponCard(setStates);

    // display info
    let onFlipCoin = OnFlipCoin(setStates);
    let onDisplayMessage = OnDisplayMessage(setStates);
    let onGameOver = OnGameOver(setStates);

    socket.on("connect", onConnect);
    socket.on("disconnect", onDisconnect);
    socket.on("prompt_user_activate", onPromptUserActivate);
    socket.on("prompt_user_select", onPromptUserSelect);
    socket.on("prompt_user_select_multiple", onPromptUserSelectMultiple);
    socket.on("prompt_user_select_text", onPromptUserSelectText);
    socket.on("prompt_user_select_board", onPromptUserSelectBoard);

    socket.on("take_damage", onTakeDamage);
    socket.on("oppon_take_damage", onOpponTakeDamage);
    socket.on("pay_mana", onPayMana);
    socket.on("oppon_pay_mana", onOpponPayMana);
    socket.on("restore_mana", onRestoreMana);
    socket.on("oppon_restore_mana", onOpponRestoreMana);
    socket.on("move_card", onMoveCard);
    socket.on("move_oppon_card", onMoveOpponCard);

    socket.on("flip_coin", onFlipCoin);
    socket.on("display_message", onDisplayMessage);
    socket.on("game_over", onGameOver);

    return () => {
      socket.off("connect", onConnect);
      socket.off("disconnect", onDisconnect);
      socket.off("prompt_user_activate", onPromptUserActivate);
      socket.off("prompt_user_select", onPromptUserSelect);
      socket.off("prompt_user_select_multiple", onPromptUserSelectMultiple);
      socket.off("prompt_user_select_text", onPromptUserSelectText);
      socket.off("prompt_user_select_board", onPromptUserSelectBoard);

      socket.off("take_damage", onTakeDamage);
      socket.off("oppon_take_damage", onOpponTakeDamage);
      socket.off("pay_mana", onPayMana);
      socket.off("oppon_pay_mana", onOpponPayMana);
      socket.off("restore_mana", onRestoreMana);
      socket.off("oppon_restore_mana", onOpponRestoreMana);
      socket.off("move_card", onMoveCard);
      socket.off("move_oppon_card", onMoveOpponCard);

      socket.off("flip_coin", onFlipCoin);
      socket.off("display_message", onDisplayMessage);
      socket.off("game_over", onGameOver);
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
        <PlayerStats owner={true} hp={ownerStats.hp} />
        <PlayerStats owner={false} hp={opponStats.hp} />
        <PlayerMana owner={true} mana={ownerStats.mana} manaMax={ownerStats.manaMax} />
        <PlayerMana owner={false} mana={opponStats.mana} manaMax={opponStats.manaMax} />
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
