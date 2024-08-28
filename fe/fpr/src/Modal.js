import React from 'react';
import './Modal.css';

import { Card } from './components/Card';

export function Modal(props) {
  let { modalState, cardCache, setHoverCard } = props;
  let { modalVisible, setModalVisible } = props;
  let {
    cards,
    title,
    transformCard,
    onClickCard,
    onClickOK,
    highlightIds,
    isDraggable,
    visibleCardId,
  } = modalState;

  if (onClickCard === undefined) {
    onClickCard = card => {};
  }
  if (transformCard === undefined) {
    transformCard = card => card;
  }
  if (highlightIds === undefined) {
    highlightIds = [];
  }

  let displayCard = card =>
    <Card id={card.id} key={"card"+card.id} card={card}
            cardCache={cardCache}
            setHoverCard={setHoverCard}
            onClick={() => onClickCard(card)}
            highlight={highlightIds && highlightIds.includes(card.id)}
            isDraggable={isDraggable}
            style={{margin: "20px", marginBottom: "35px", scale: "120%",
                    visibility: visibleCardId === card.id? "visible" : "inherit"}}
      />;
  return (
    <div class="modal" style={{visibility: modalVisible? "visible": "hidden"}} >
      <button class="exit-button" onClick={() => setModalVisible(false)}>X</button>
      <h1 class="modal-title">{title}</h1>
      {cards.map(transformCard).map(displayCard)}
      {onClickOK && <button class="modal-ok-button" onClick={onClickOK}>OK</button>}
    </div>
  );
}
