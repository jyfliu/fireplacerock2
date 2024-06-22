import React from 'react';

import './HoverCard.css';

export function HoverCard(props) {
  const { hoverCard, setHoverCard } = props;
  const { card, inCard, inHoverCard, inDrag } = hoverCard;
  console.log("inCard", inCard, "inHoverCard", inHoverCard, "inDrag", inDrag);
  if (!card || !card.name || inDrag) {
    return null;
  }
  if (!inCard && !inHoverCard) {
    return null;
  }

  const enterHover = () => setHoverCard(hoverCard => ({...hoverCard, inHoverCard: true}));
  const leaveHover = () => setHoverCard(hoverCard => ({...hoverCard, inHoverCard: false}));

  return (
    <div class="hc-card" onMouseOver={enterHover} onMouseLeave={leaveHover} >
      <h2 class="hc-title">{card.name}</h2>
      <h4 class="hc-description">{card.description}</h4>
      <h4 class="hc-attack">{card.attack}</h4>
      <h4 class="hc-health">{card.health}</h4>
      <h4 class="hc-cost">{card.cost}</h4>
    </div>
  );
}

