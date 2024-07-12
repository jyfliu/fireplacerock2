import React from 'react';
import { useDraggable } from '@dnd-kit/core';

import './Card.css';


export function Card(props) {
  const { card, setHoverCard } = props;
  const { phase, activateBoard, boardId } = props;

  const enterCard = () => setHoverCard(hoverCard => ({...hoverCard, card: card, inCard: true}));
  const leaveCard = () => setHoverCard(hoverCard => ({...hoverCard, inCard: false}));

  let {attributes, listeners, setNodeRef, transform} = useDraggable({
    id: props.id,
  });

  let isDraggable = false;
  let onClick = () => {};
  if (phase[0] === "owner") {
    if (phase[1] === "battle" || !activateBoard) {
      isDraggable = true;
    }
    if (activateBoard && phase[0] === "owner" && phase[1] !== "battle") {
      // for some reason doesn't work with draggable -- debug with internet
      if ([10, 11, 12, 13, 14].includes(boardId)) {
        onClick = () => activateBoard(boardId - 10);
      }
    }
  }

  const style = {
    "transform": transform?
      `perspective(1000px) translate3d(${transform.x}px, ${transform.y*0.86602540378}px, 0) ${card.isSelected? "rotateX(30deg)" : ""}`
    : undefined
  };

  return (
    <button class="card" ref={setNodeRef} style={style}
            {...(isDraggable && listeners)}
            {...(isDraggable && attributes)}
            onMouseOver={enterCard}
            onMouseLeave={leaveCard}
            onClick={onClick}
    >
      <h3>{card.name}</h3>
      <h4 class="attack">{card.attack}</h4>
      <h4 class="health">{card.health}</h4>
      <h4 class="cost">{card.cost}</h4>
    </button>
  );
}

export function Deck(props) {
  let { name, count, cards } = props;
  if (count === undefined && cards !== undefined) {
    count = cards.length;
  }
  let onClick = () => {};
  if (cards !== undefined) {
    let cardsStr = name + ":\n" + (
      cards
        .map(card => `[${card.name}]`)
        .join("\n")
    );
    onClick = () => alert(cardsStr);
  }
  return (
    <button class="card" onClick={onClick} >
      <h4>{name}</h4>
      <h1>{count}</h1>
    </button>
  );
}
