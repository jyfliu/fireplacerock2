import React from 'react';
import { useDraggable } from '@dnd-kit/core';

import './Card.css';
import { pSBC } from '../Utils.js';


export function Card(props) {
  const { card, setHoverCard, style } = props;
  const { isDraggable, onClick, cardCache } = props;

  const enterCard = () => setHoverCard(hoverCard => ({...hoverCard, card: card, inCard: true}));
  const leaveCard = () => setHoverCard(hoverCard => ({...hoverCard, inCard: false}));

  let {attributes, listeners, setNodeRef, transform} = useDraggable({
    id: props.id,
  });

  const hasSprite = cardCache[card.template_id];
  const colour = card.bkgd_colour? pSBC(0.50, `rgba(${Math.round(card.bkgd_colour[0])},${Math.round(card.bkgd_colour[1])},${Math.round(card.bkgd_colour[2])}, 0.5)`) : "lightgrey";
  const bkgd_colour = card.bkgd_colour? pSBC(0.2, `rgba(${Math.round(card.bkgd_colour[0])},${Math.round(card.bkgd_colour[1])},${Math.round(card.bkgd_colour[2])}, 255)`) : "lightgrey";

  const renderSprite = () => {
    if (!hasSprite) return null;
    const { image, isMini } = cardCache[card.template_id];
    if (!isMini) {
      return <img class="sprite" src={image.src} alt=""/>;
    } else {
      return (<>
        <img class="mini-sprite" src={image.src} alt=""/>
        <div class="description" style={{backgroundColor: colour}}>
        <hr/>
        <hr/>
        <hr/>
        </div>
      </>);
    }
  };

  const fullStyle = {
    "transform": transform?
      `perspective(1000px) translate3d(${transform.x}px, ${transform.y*0.86602540378}px, 0) ${card.isSelected? "rotateX(30deg)" : ""}`
    : undefined,
    "background-color": bkgd_colour,
    ...style,
  };

  return (
    <button class="card" ref={setNodeRef} style={fullStyle}
            {...(isDraggable && listeners)}
            {...(isDraggable && attributes)}
            onMouseOver={enterCard}
            onMouseLeave={leaveCard}
            onClick={onClick}
    >
      {card.name && <h3 class="name" >{card.name}</h3>}
      {cardCache[card.template_id] && renderSprite()}
      {card.attack!==undefined && <h4 class="attack">{card.attack}</h4>}
      {card.health!==undefined && <h4 class="health">{card.health}</h4>}
      {card.cost !== undefined && <h4 class="cost">{card.cost}</h4>}
    </button>
  );
}

export function Deck(props) {
  let { name, count, cards, displayCards } = props;
  if (count === undefined && cards !== undefined) {
    count = cards.length;
  }
  let onClick = () => {};
  if (cards !== undefined && displayCards !== undefined) {
    onClick = () => displayCards(cards);
  }
  return (
    <button class="card" onClick={onClick} >
      <h4>{name}</h4>
      <h1>{count}</h1>
    </button>
  );
}
