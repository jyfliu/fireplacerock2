import React, { useState, useEffect } from 'react';
import { DndContext } from '@dnd-kit/core';

import { socket } from './socket';

import { BoardSpace } from './components/BoardSpace';
import { Card } from './components/Card';
import { ChatBox } from './components/ChatBox';
import { PlayerStats, PlayerMana } from './components/PlayerStats';

import { CanSummon, CanAttack } from "./GameState"

import {
  OnPromptUserActivate, OnPromptUserSelectCards,
  OnPromptUserSelectText, OnPromptUserSelectBoard,
  OnBeginPhase, OnEndTurn,
  OnTakeDamage, OnOpponTakeDamage, OnPayMana, OnOpponPayMana,
  OnRestoreMana, OnOpponRestoreMana, OnMoveCard, OnMoveOpponCard,
  OnFlipCoin, OnDisplayMessage,
  OnGameStart, OnGameOver,
  OnCardChangeName, OnCardGain, OnCardLose, OnCardTakeDamage, OnCardSet,
} from "./GatewayIn"

import {
  EmitNextPhase, EmitNextTurn,
  Summon, Attack, AttackDirectly,
} from "./GatewayOut"

import './App.css';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [chat, setChat] = useState([]);
  const pushChat = msg => {
    setChat(chatLog => chatLog.concat([msg]));
  }

  const [phase, setPhase] = useState(["owner", "draw"]);
  const [hasInitiative, setHasInitiative] = useState(false);
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
  const [field, setField] = useState({
    opponTraps:    [null, null, null, null, null],
    opponMonsters: [null, null, null, null, null],
    ownerMonsters: [null, null, null, null, null],
    ownerTraps:    [null, null, null, null, null],
  });
  const [ownerCards, setOwnerCards] = useState({
    ownerGraveyard: [],
    ownerBanished: [],
    ownerMainDeck: 0,
    ownerExtraDeck: [],
  })
  const [opponCards, setOpponCards] = useState({
    opponGraveyard: [],
    opponBanished: [],
    opponMainDeck: 0,
    opponExtraDeck: 0,
  })

  const states = {
    chat: chat,
    ownerHand: ownerHand,
    opponHand: opponHand,
    ownerCards: ownerCards,
    opponCards: opponCards,
    phase: phase,
    hasInitiative: hasInitiative,
    field: field,
    ownerStats: ownerStats,
    opponStats: opponStats,
  }

  let canSummon = CanSummon(states);
  let canAttack = CanAttack(states);

  let emitNextTurn = EmitNextTurn(socket);
  let emitNextPhase = EmitNextPhase(socket);
  let summon = Summon(socket);
  let attack = Attack(socket);
  let attackDirectly = AttackDirectly(socket);

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

    const setStates = {
      pushChat: pushChat,
      setOwnerHand: setOwnerHand,
      setOpponHand: setOpponHand,
      setOwnerCards: setOwnerCards,
      setOpponCards: setOpponCards,
      setPhase: setPhase,
      setHasInitiative: setHasInitiative,
      setField: setField,
      setOwnerStats: setOwnerStats,
      setOpponStats: setOpponStats,
    };

    // query user input
    let onPromptUserActivate = OnPromptUserActivate(setStates);
    let onPromptUserSelectCards = OnPromptUserSelectCards(setStates);
    let onPromptUserSelectText = OnPromptUserSelectText(setStates);
    let onPromptUserSelectBoard = OnPromptUserSelectBoard(setStates);

    // update state functions
    let onBeginPhase = OnBeginPhase(setStates);
    let onEndTurn = OnEndTurn(setStates);

    let onTakeDamage = OnTakeDamage(setStates);
    let onOpponTakeDamage = OnOpponTakeDamage(setStates);
    let onPayMana = OnPayMana(setStates);
    let onOpponPayMana = OnOpponPayMana(setStates);
    let onRestoreMana = OnRestoreMana(setStates);
    let onOpponRestoreMana = OnOpponRestoreMana(setStates);

    let onMoveCard = OnMoveCard(setStates);
    let onMoveOpponCard = OnMoveOpponCard(setStates);

    let onCardChangeName = OnCardChangeName(setStates);
    let onCardGain = OnCardGain(setStates);
    let onCardLose = OnCardLose(setStates);
    let onCardTakeDamage = OnCardTakeDamage(setStates);
    let onCardSet = OnCardSet(setStates);

    // display info
    let onFlipCoin = OnFlipCoin(setStates);
    let onDisplayMessage = OnDisplayMessage(setStates);
    let onGameStart = OnGameStart(setStates);
    let onGameOver = OnGameOver(setStates);

    socket.on("connect", onConnect);
    socket.on("disconnect", onDisconnect);
    socket.on("prompt_user_activate", onPromptUserActivate);
    socket.on("prompt_user_select_cards", onPromptUserSelectCards);
    socket.on("prompt_user_select_text", onPromptUserSelectText);
    socket.on("prompt_user_select_board", onPromptUserSelectBoard);

    socket.on("begin_phase", onBeginPhase);
    socket.on("end_turn", onEndTurn);

    socket.on("take_damage", onTakeDamage);
    socket.on("oppon_take_damage", onOpponTakeDamage);
    socket.on("pay_mana", onPayMana);
    socket.on("oppon_pay_mana", onOpponPayMana);
    socket.on("restore_mana", onRestoreMana);
    socket.on("oppon_restore_mana", onOpponRestoreMana);
    socket.on("move_card", onMoveCard);
    socket.on("move_oppon_card", onMoveOpponCard);

    socket.on("card_change_name", onCardChangeName);
    socket.on("card_gain", onCardGain);
    socket.on("card_lose", onCardLose);
    socket.on("card_take_damage", onCardTakeDamage);
    socket.on("card_set", onCardSet);

    socket.on("flip_coin", onFlipCoin);
    socket.on("display_message", onDisplayMessage);
    socket.on("game_start", onGameStart);
    socket.on("game_over", onGameOver);

    return () => {
      socket.off("connect", onConnect);
      socket.off("disconnect", onDisconnect);
      socket.off("prompt_user_activate", onPromptUserActivate);
      socket.off("prompt_user_select_cards", onPromptUserSelectCards);
      socket.off("prompt_user_select_text", onPromptUserSelectText);
      socket.off("prompt_user_select_board", onPromptUserSelectBoard);

      socket.off("begin_phase", onBeginPhase);
      socket.off("end_turn", onEndTurn);

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
      socket.off("game_start", onGameStart);
      socket.off("game_over", onGameOver);
    };
  }, []);


  // board state
  const containers = [
    0, 1, 2, 3, 4,
    5, 6, 7, 8, 9,
    10, 11, 12, 13, 14,
    15, 16, 17, 18, 19
  ];



  // display helpers
  const displayCard = card =>
    <Card id={card.id} key={"card"+card.id} card={card} inDroppable={false} />


  const statusStyle = {
    "color": isConnected? "green" : "red"
  }

  return (
    <DndContext onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
      <p style={statusStyle} class="status-bar">
        {isConnected ? "Connected: ip=0.0.0.0:9069" : "Disconnected"}
      </p>
      <ChatBox chat={chat} />
      <div class="battle">
        <div class="oppon-hand">
          {
            Array.from(Array(opponHand).keys()).map(id => ({
              id: "oppon" + id,
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
          <button onClick={emitNextPhase}>Next Phase</button>
          <button onClick={emitNextTurn} class="end-button">End Turn</button>
        </div>
        <div class="board-grid">
          {containers.map((id) => {
            // We updated the Droppable component so it would accept an `id`
            // prop and pass it to `useDroppable`
            let cardsOnSquare = ownerHand.filter(card => card.parent === id);
            if ([0, 1, 2, 3, 4].includes(id) && field.opponTraps[id] != null) {
              cardsOnSquare.push(field.opponTraps[id]);
            }
            if ([5, 6, 7, 8, 9].includes(id) && field.opponMonsters[id - 5] != null) {
              cardsOnSquare.push(field.opponMonsters[id - 5]);
            }
            if ([10, 11, 12, 13, 14].includes(id) && field.ownerMonsters[id - 10] != null) {
              cardsOnSquare.push(field.ownerMonsters[id - 10]);
            }
            if ([15, 16, 17, 18, 19].includes(id) && field.ownerTraps[id - 15] != null) {
              cardsOnSquare.push(field.ownerTraps[id - 15]);
            }
            let cardsSelected = ownerHand.filter(card => card.isSelected);
            let hiColor = "#000000";
            if (cardsSelected.length > 0) {
              let card = cardsSelected[0];
              let cardCanSummon = canSummon(card) && [10, 11, 12, 13, 14].includes(id);
              hiColor = cardCanSummon? "#449944" : "#994444";
            }

            return (
              <div class="card-griditem">
                <BoardSpace key={"board"+id} id={id} hiColor={hiColor}>
                  {cardsOnSquare.length > 0? displayCard(cardsOnSquare[0]) : null}
                </BoardSpace>
              </div>
            )
          })}
        </div>
        <div class="owner-hand">
          {ownerHand.filter(card => card.parent === null).map(displayCard)}
        </div>
      </div>
    </DndContext>
  );

  function handleDragStart(event) {
    const { active } = event;

    setOwnerHand(ownerHand.map(
      card =>
        card.id === active.id?
        {...card, isSelected: true}
        : card
    ))
  }

  function handleDragEnd(event) {
    const { active, over } = event;

    // If the item is dropped over a container, set it as the parent
    // otherwise reset the parent to `null`
    setOwnerHand(ownerHand.map(
      (card, handIdx) => {
        let shouldDrop = false;
        if (
          !over
          || card.id !== active.id
          || (card.type === "monster" && ![10, 11, 12, 13, 14].includes(over.id))
          || (card.type === "spell" && ![15, 16, 17, 18, 19].includes(over.id))
        ) {
          return {...card, isSelected: false};
        }
        if (card.type === "monster") {
          let idx = over.id - 10;
          if (field.ownerMonsters[idx] != null) {
            return {...card, isSelected: false};
          }
          summon(handIdx, idx)
        }
        if (card.type === "spell") {
          let idx = card.id - 10;
          if (field.ownerTraps[idx] != null) {
            return {...card, isSelected: false};
          }
        }

        shouldDrop |= card.type === "monster" && canSummon(card);
        shouldDrop |= card.type === "spell" && card.can_activate;
        if (shouldDrop) {
          return {...card, parent: over? over.id : null, isSelected: false};
        } else {
          return {...card, isSelected: false};
        }
      }
    ));

    setField({
      ...field,
      ownerMonsters: field.ownerMonsters.map(
        (card, boardIdx) => {
          if (!card) { return card; }
          if (
            card.id !== active.id
            || card.type !== "monster"
            || ![5, 6, 7, 8, 9].includes(over.id)
          ) {
            return {...card, isSelected: false};
          }
          if (card.type === "monster" && over) {
            let idx = over.id - 5;
            if (field.opponMonsters[idx] !== null) {
              attack(boardIdx, idx);
              if (canAttack(card)) {
                // TODO animate differently
              }
              return {...card, isSelected: false};
            }
          }
          // else attack directly
          attackDirectly(boardIdx);
          return {...card, isSelected: false};
        }
      )
    });
  }
};

export default App;
