import React, { useState, useEffect } from 'react';
import useCookie from 'react-use-cookie';
import { DndContext, DragOverlay } from '@dnd-kit/core';

import { socket } from './socket';

import { Modal } from './Modal';
import { BoardSpace } from './components/BoardSpace';
import { Card, Deck } from './components/Card';
import { ChatBox } from './components/ChatBox';
import { HoverCard } from './components/HoverCard';
import { PlayerStats, PlayerMana } from './components/PlayerStats';

import {
  CanSummon, CanSummonExtraDeck,
  CanActivateHand, CanAttack
} from "./GameState"

import {
  OnInitGameState,
  OnPromptUserActivate, OnPromptUserSelectCards,
  OnPromptUserSelectText, OnPromptUserSelectBoard,
  OnBeginPhase, OnEndTurn,
  OnTakeDamage, OnOpponTakeDamage, OnHeal, OnOpponHeal,
  OnPayMana, OnOpponPayMana,
  OnRestoreMana, OnOpponRestoreMana, OnMoveCard, OnMoveOpponCard,
  OnFlipCoin, OnDisplayMessage,
  OnGameStart, OnGameOver,
  OnCardChangeName, OnCardGain, OnCardLose, OnCardTakeDamage, OnCardSet,
} from "./GatewayIn"

import {
  EmitNextPhase, EmitNextTurn,
  Summon, SummonExtraDeck, ActivateSpell,
  Attack, AttackDirectly,
  ActivateBoard, ActivateFieldSpell,
} from "./GatewayOut"

import { vmin, inches } from './Utils.js';
import './Game.css';

const defaultHoverCard = {
  card: {},
  inCard: false,
  inHoverCard: false,
  inDrag: false,
};

const defaultModalState = {
  cards: [],
  title: "",
  onClickCard: (card) => {},
  onClickOK: undefined,
  visibleCardId: undefined,
};

const defaultField = {
  opponTraps:    [null, null, null, null, null],
  opponMonsters: [null, null, null, null, null],
  ownerMonsters: [null, null, null, null, null],
  ownerTraps:    [null, null, null, null, null],
};

const defaultOwnerCards = {
  ownerGraveyard: [],
  ownerBanished: [],
  ownerMainDeck: 0,
  ownerExtraDeck: [],
};

const defaultOwnerHand = [];
const defaultOpponHand = 0;

const defaultOpponCards = {
  opponGraveyard: [],
  opponBanished: [],
  opponMainDeck: 0,
  opponExtraDeck: 0,
};

const defaultStats = {
  hp: 0,
  mana: 0,
  manaMax: 0,
};

function Game() {
  const [username] = useCookie("username", "");
  const [passphrase] = useCookie("passphrase", "");

  // meta state
  const [isConnected, setIsConnected] = useState(false);
  const [chat, setChat] = useState([]);
  const pushChat = msg => {
    setChat(chatLog => chatLog.concat([msg]));
  };
  const [hoverCard, setHoverCard] = useState(defaultHoverCard);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalVisibleReset, setModalVisibleReset] = useState(false);
  const [modalState, setModalState] = useState(defaultModalState);
  const [cardCache, setCardCache] = useState({});

  // game state
  const [phase, setPhase] = useState(["owner", "draw"]);
  const [hasInitiative, setHasInitiative] = useState(false);
  const [ownerHand, setOwnerHand] = useState(defaultOwnerHand);
  const [opponHand, setOpponHand] = useState(defaultOpponHand);
  const [ownerStats, setOwnerStats] = useState(defaultStats);
  const [opponStats, setOpponStats] = useState(defaultStats);
  const [field, setField] = useState(defaultField);
  const [ownerCards, setOwnerCards] = useState(defaultOwnerCards);
  const [opponCards, setOpponCards] = useState(defaultOpponCards);

  const states = {
    chat: chat,
    modalVisible: modalVisible,
    modalState: modalState,
    hoverCard: hoverCard,

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
  let canSummonExtraDeck = CanSummonExtraDeck(states);
  let canActivateHand = CanActivateHand(states);
  let canAttack = CanAttack(states);


  let emitNextTurn = EmitNextTurn(socket);
  let emitNextPhase = EmitNextPhase(socket);
  let summon = Summon(socket);
  let summonExtraDeck = SummonExtraDeck(socket);
  let activateSpell = ActivateSpell(socket);
  let attack = Attack(socket);
  let attackDirectly = AttackDirectly(socket);
  let activateBoard = ActivateBoard(socket, states);
  let activateFieldSpell = ActivateFieldSpell(socket, states);

  useEffect(() => {
    let onConnect = () => {
      setIsConnected(true);

      socket.emit("login", username, passphrase)
      if (username) {
        let oppo = prompt("Who would you like to challenge?");
        socket.emit("challenge", oppo)
      }

      setHoverCard(defaultHoverCard);
      setModalState(defaultModalState);
      setModalVisible(false);
      setModalVisibleReset(false);
      setField(defaultField);
      setOwnerHand(defaultOwnerHand);
      setOpponHand(defaultOpponHand);
      setOwnerCards(defaultOwnerCards);
      setOpponCards(defaultOpponCards);
      setOwnerStats(defaultStats);
      setOpponStats(defaultStats);

    };
    let onDisconnect = () => {
      setIsConnected(false);
    };

    const setStates = {
      pushChat: pushChat,
      setHoverCard: setHoverCard,
      setModalVisible: setModalVisible,
      setModalState: setModalState,
      setCardCache: setCardCache,

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

    let onInitGameState = OnInitGameState(setStates);

    // query user input
    let onPromptUserActivate = OnPromptUserActivate(setStates);
    let onPromptUserSelectCards = OnPromptUserSelectCards(setStates);
    let onPromptUserSelectText = OnPromptUserSelectText(setStates);
    let onPromptUserSelectBoard = OnPromptUserSelectBoard(setStates);

    // update state functions
    let onBeginPhase = OnBeginPhase(setStates);
    let onEndTurn = OnEndTurn(setStates);

    let onTakeDamage = OnTakeDamage(setStates);
    let onOpponTakeDamage = OnOpponTakeDamage(setStates)
    let onHeal = OnHeal(setStates);
    let onOpponHeal = OnOpponHeal(setStates);;
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
    socket.on("init_game_state", onInitGameState);

    socket.on("prompt_user_activate", onPromptUserActivate);
    socket.on("prompt_user_select_cards", onPromptUserSelectCards);
    socket.on("prompt_user_select_text", onPromptUserSelectText);
    socket.on("prompt_user_select_board", onPromptUserSelectBoard);

    socket.on("begin_phase", onBeginPhase);
    socket.on("end_turn", onEndTurn);

    socket.on("take_damage", onTakeDamage);
    socket.on("oppon_take_damage", onOpponTakeDamage);
    socket.on("heal", onHeal);
    socket.on("oppon_heal", onOpponHeal);
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
      socket.off("init_game_state", onInitGameState);

      socket.off("prompt_user_activate", onPromptUserActivate);
      socket.off("prompt_user_select_cards", onPromptUserSelectCards);
      socket.off("prompt_user_select_text", onPromptUserSelectText);
      socket.off("prompt_user_select_board", onPromptUserSelectBoard);

      socket.off("begin_phase", onBeginPhase);
      socket.off("end_turn", onEndTurn);

      socket.off("take_damage", onTakeDamage);
      socket.off("oppon_take_damage", onOpponTakeDamage);
      socket.off("heal", onHeal);
      socket.off("oppon_heal", onOpponHeal);
      socket.off("pay_mana", onPayMana);
      socket.off("oppon_pay_mana", onOpponPayMana);
      socket.off("restore_mana", onRestoreMana);
      socket.off("oppon_restore_mana", onOpponRestoreMana);
      socket.off("move_card", onMoveCard);
      socket.off("move_oppon_card", onMoveOpponCard);

      socket.off("card_change_name", onCardChangeName);
      socket.off("card_gain", onCardGain);
      socket.off("card_lose", onCardLose);
      socket.off("card_take_damage", onCardTakeDamage);
      socket.off("card_set", onCardSet);

      socket.off("flip_coin", onFlipCoin);
      socket.off("display_message", onDisplayMessage);
      socket.off("game_start", onGameStart);
      socket.off("game_over", onGameOver);
    };
  }, [username, passphrase]);

  if (!username) {
    return <div>Error, not logged in?</div>;
  }


  // board state
  const containers = [
    0, 1, 2, 3, 4,
    5, 6, 7, 8, 9,
    10, 11, 12, 13, 14,
    15, 16, 17, 18, 19
  ];



  // display helpers
  const cardScale = {zoom: vmin(8.05) / inches(4.6) + "", transformOrigin: "top left"};
  const displayCard = (card, isDraggable) =>
    <Card id={card.id} key={"card"+card.id} card={card} inDroppable={false}
          cardCache={cardCache}
          isDraggable={isDraggable}
          setHoverCard={setHoverCard}
      />;
  const displayCardOnBoard = (card, onClick, isDraggable) =>
    <Card id={card.id} key={"card"+card.id} card={card} inDroppable={false}
          cardCache={cardCache}
          onClick={onClick} isDraggable={isDraggable}
          style={cardScale}
          setHoverCard={setHoverCard} />;
  const displayCardsInModal = cards => {
    setModalVisible(true);
    setModalState({
      cards: cards,
      title: ""
    });
  };
  const displayCardsInModalFromExtraDeck = cards => {
    setModalVisible(true);
    setModalState({
      cards: cards,
      title: "",
      isDraggable: true,
    });
  };


  const statusStyle = {
    "color": isConnected? "green" : "red"
  }
  const URL = process.env.NODE_ENV === 'production' ? 'https://gamesby.jeffr.ee:8443' : 'http://localhost:8443';

  return (
    <DndContext onDragStart={handleDragStart} onDragEnd={handleDragEnd} >
      <p style={statusStyle} class="status-bar">
        {isConnected ? `Connected: ip=${URL}` : "Disconnected"}
      </p>
      <div class="phase-indicator">
        <button class="phase-indicator-button">
          {phase[0] === "owner"? "Your" : "Your opponent's"}<br />{phase[1]} phase
        </button>
      </div>
      <div class="phase-select">
        <button onClick={emitNextPhase} class="next-button">Next Phase</button>
        <button onClick={emitNextTurn} class="end-button">End Turn</button>
      </div>
      <PlayerStats owner={true} hp={ownerStats.hp} />
      <PlayerStats owner={false} hp={opponStats.hp} />
      <PlayerMana owner={true} mana={ownerStats.mana} manaMax={ownerStats.manaMax} />
      <PlayerMana owner={false} mana={opponStats.mana} manaMax={opponStats.manaMax} />
      <ChatBox chat={chat} />
      <HoverCard hoverCard={hoverCard} setHoverCard={setHoverCard} cardCache={cardCache} />
      <DragOverlay>
      </DragOverlay>
      <div class="battle">
        <Modal modalState={modalState}
               setHoverCard={setHoverCard}
               modalVisible={modalVisible}
               setModalVisible={setModalVisible}
               cardCache={cardCache} />
        <div class="oppon-hand" style={{zoom: vmin(10) / inches(4.6) + ""}}>
          {
            Array.from(Array(opponHand).keys()).map(id => ({
              id: "oppon" + id,
              name: "",
              parent: null,
            })).map(displayCard)
          }
        </div>
        <div class="board">
          <div class="decks">
            <Deck name="Opponent's Graveyard" cards={opponCards.opponGraveyard} displayCards={displayCardsInModal} style={cardScale}/>
            <Deck name="Opponent's Banished" cards={opponCards.opponBanished} displayCards={displayCardsInModal} style={cardScale}/>
            <Deck name="Extra Deck" cards={ownerCards.ownerExtraDeck} displayCards={displayCardsInModalFromExtraDeck} style={cardScale}/>
            <Deck name="Deck" count={ownerCards.ownerMainDeck} style={cardScale}/>
          </div>
          <div class="board-grid" >
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
                let shouldHighlight = canSummon(card) && [10, 11, 12, 13, 14].includes(id);
                shouldHighlight ||= canActivateHand(card) && [10, 11, 12, 13, 14].includes(id);
                hiColor = shouldHighlight? "#449944" : "#994444";
              }

              let isDraggable = false;
              let onClick = () => {};
                if (phase && phase[0] === "owner") {
                  if (phase[1] === "battle" || !activateBoard) {
                    isDraggable = true;
                  }
                  if (phase[0] === "owner" && phase[1] !== "battle") {
                    // for some reason doesn't work with draggable -- debug with internet
                    if ([10, 11, 12, 13, 14].includes(id)) {
                      onClick = () => activateBoard(id - 10);
                    }
                  }
                  if (phase[0] === "owner" && phase[1] !== "battle") {
                    if ([15, 16, 17, 18, 19].includes(id)) {
                      onClick = () => activateFieldSpell(id - 15);
                    }
                  }
                }

              return (
                <div class="card-griditem">
                  <BoardSpace key={"board"+id} id={id} hiColor={hiColor}>
                    {cardsOnSquare.length > 0? displayCardOnBoard(cardsOnSquare[0], onClick, isDraggable) : null}
                  </BoardSpace>
                </div>
              )
            })}
          </div>
          <div class="decks">
            <Deck name="Opponent's Deck" count={opponCards.opponMainDeck} style={cardScale} />
            <Deck name="Opponent's Extra Deck" count={opponCards.opponExtraDeck} style={cardScale}/>
            <Deck name="Banished" cards={ownerCards.ownerBanished} displayCards={displayCardsInModal} style={cardScale}/>
            <Deck name="Graveyard" cards={ownerCards.ownerGraveyard} displayCards={displayCardsInModal} style={cardScale}/>
          </div>
        </div>
        <div class="owner-hand" style={{zoom: vmin(12) / inches(4.6) + ""}}>
          {ownerHand.filter(card => card.parent === null).map(card => displayCard(card, true))}
        </div>
      </div>
      <img class="bkgd-img" src="/assets/images/tft.jpg" alt="" />
    </DndContext>
  );

  function handleDragStart(event) {
    const { active } = event;
    const selectCardIf = card =>
        card.id === active.id?
          {...card, isSelected: true }
          : card;

    setHoverCard(hoverCard => ({...hoverCard, inDrag: true}));
    setOwnerHand(ownerHand.map(selectCardIf));
    setOwnerCards(cards => ({
      ...cards,
      ownerExtraDeck: cards.ownerExtraDeck.map(selectCardIf),
    }));
    setModalVisibleReset(modalVisible);
    if (modalVisible) {
      setModalState(state => ({
        ...state,
        visibleCardId: active.id,
        transformCard: selectCardIf,
      }));
      setModalVisible(false);
    }
  }

  function handleDragEnd(event) {
    const { active, over } = event;

    const resetCard = card => ({...card, isSelected: false });
    const prefix = modalVisibleReset? "modal" : ""

    setHoverCard(hoverCard => ({...hoverCard, inCard: false, inDrag: false}));
    // If the item is dropped over a container, set it as the parent
    // otherwise reset the parent to `null`
    setOwnerHand(ownerHand.map(
      (card, handIdx) => {
        let shouldDrop = false;
        if (!card) {
          return card;
        }
        if (
          !over
          || card.id !== active.id
          || (card.type === "monster" && ![10, 11, 12, 13, 14].includes(over.id))
          || (card.type === "spell" && ![15, 16, 17, 18, 19].includes(over.id))
        ) {
          return resetCard(card);
        }
        if (card.type === "monster") {
          let idx = over.id - 10;
          if (![10, 11, 12, 13, 14].includes(over.id) || field.ownerMonsters[idx] != null) {
            return resetCard(card);
          }
          summon(handIdx, idx)
        }
        if (card.type === "spell" || card.type === "field spell") {
          let idx = over.id - 15;
          if (![15, 16, 17, 18, 19].includes(over.id) || field.ownerTraps[idx] != null) {
            return resetCard(card);
          }
          activateSpell(handIdx, idx);
        }

        shouldDrop |= card.type === "monster" && canSummon(card);
        shouldDrop |= card.type === "spell" && card.can_activate;
        if (shouldDrop) {
          return {...resetCard(card), parent: over? over.id : null};
        } else {
          return resetCard(card);
        }
      }
    ));

    const ownerExtraDeck = ownerCards.ownerExtraDeck.map(
      (card, extraDeckIdx) => {
        let shouldDrop = false;
        if (!card) {
          return card;
        }
        if (
          !over
          || prefix + card.id !== active.id
          || (card.type === "monster" && ![10, 11, 12, 13, 14].includes(over.id))
        ) {
          return resetCard(card);
        }
        if (card.type === "monster") {
          let idx = over.id - 10;
          if (![10, 11, 12, 13, 14].includes(over.id) || field.ownerMonsters[idx] != null) {
            return resetCard(card);
          }
          summonExtraDeck(extraDeckIdx, idx)
        }

        shouldDrop |= card.type === "monster" && canSummonExtraDeck(card);
        if (shouldDrop) {
          return {...resetCard(card), parent: over? over.id : null };
        } else {
          return resetCard(card);
        }
      });

    setOwnerCards(cards => ({
      ...cards,
      ownerExtraDeck: ownerExtraDeck,
    }));

    setField({
      ...field,
      ownerMonsters: field.ownerMonsters.map(
        (card, boardIdx) => {
          if (!card) { return card; }

          if (
            prefix + card.id !== active.id
            || card.type !== "monster"
          ) {
            return resetCard(card);
          }
          console.log("HI")
          if (card.type === "monster" && over) {
            let idx = over.id - 5;
            if (field.opponMonsters[idx]) {
              attack(boardIdx, idx);
              if (canAttack(card)) {
                // TODO animate differently
              }
              return resetCard(card);
            }
          }
          console.log("attack i")
          // else attack directly
          attackDirectly(boardIdx);
          return resetCard(card);
        }
      )
    });

    setModalVisible(modalVisibleReset);
    setModalVisibleReset(false);
    setModalState(state => ({
      ...state,
      visibleCardId: undefined,
      transformCard: undefined,
    }));
  }
};

export default Game;
