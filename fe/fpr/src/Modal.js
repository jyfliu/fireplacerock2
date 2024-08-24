import React from 'react';
import './Modal.css';

import { Card } from './components/Card';

export function Modal(props) {
  let { modalState, cardCache, setHoverCard } = props;
  let { modalVisible, setModalVisible } = props;
  let { cards, title, onClickCard, onClickOK, highlightIds } = modalState;
  if (!modalVisible) {
    return;
  }

  if (onClickCard === undefined) {
    onClickCard = card => {};
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
            style={{margin: "30px", scale: "150%"}}
      />;
  return (
    <div class="modal">
      <button class="exit-button" onClick={() => setModalVisible(false)}>X</button>
      <h1 class="modal-title">{title}</h1>
      {cards.map(displayCard)}
      {onClickOK && <button class="modal-ok-button" onClick={onClickOK}>OK</button>}
    </div>
  );
}
