import React from 'react';
import { useDraggable } from '@dnd-kit/core';

import './Card.css';


export function Card(props) {
  const {attributes, listeners, setNodeRef, transform} = useDraggable({
    id: props.id,
  });
  const { inDroppable, card } = props;
  const style = {
    "transform": transform?
      `perspective(1000px) translate3d(${transform.x}px, ${transform.y*0.86602540378}px, 0) ${inDroppable? "rotateX(30deg)" : ""}`
    : undefined
  };


  return (
    <button class="card" ref={setNodeRef} style={style} {...listeners} {...attributes}>
      <h3>{card.name}</h3>
      <h4 class="attack">{card.attack}</h4>
      <h4 class="health">{card.health}</h4>
      <h4 class="cost">{card.cost}</h4>
    </button>
  );
}
