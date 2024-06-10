import React from 'react';

import './HoverCard.css';

export function HoverCard(props) {
  const { card } = props;
  if (!card) {
    return null;
  }

  return (
    <div class="card">
      <h2>{card.name}</h2>
      <h4>{card.description}</h4>
      <h4 class="attack">{card.attack}</h4>
      <h4 class="health">{card.health}</h4>
      <h4 class="cost">{card.cost}</h4>
    </div>
  );
}
