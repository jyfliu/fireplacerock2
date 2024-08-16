import React from 'react';
import './Modal.css';

import { Card } from './components/Card';

export function Modal(props) {
  let { cards, cardCache, setHoverCard } = props;
  let { modalVisible, setModalVisible } = props;
  if (!modalVisible) {
    return;
  }

  let displayCard = card =>
    <Card id={card.id} key={"card"+card.id} card={card}
            cardCache={cardCache}
            setHoverCard={setHoverCard}
            style={{margin: "30px", scale: "150%"}}
      />;
  return (
    <div class="modal">
      <button class="exit-button" onClick={() => setModalVisible(false)}>X</button>
      {cards.map(displayCard)}
    </div>
  );
}
