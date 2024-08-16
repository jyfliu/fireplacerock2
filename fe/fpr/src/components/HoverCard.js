import React from 'react';

import './HoverCard.css';
import { pSBC } from '../Utils.js';


export function HoverCard(props) {
  const { hoverCard, setHoverCard, cardCache } = props;
  const { card, inCard, inHoverCard, inDrag } = hoverCard;
  if (!card || !card.name || inDrag) {
    return null;
  }
  if (!inCard && !inHoverCard) {
    return null;
  }

  const enterHover = () => setHoverCard(hoverCard => ({...hoverCard, inHoverCard: true}));
  const leaveHover = () => setHoverCard(hoverCard => ({...hoverCard, inHoverCard: false}));
  const colour = pSBC(0.50, `rgba(${Math.round(card.bkgd_colour[0])},${Math.round(card.bkgd_colour[1])},${Math.round(card.bkgd_colour[2])}, 0.8)`);
  const bkgd_colour = pSBC(0.2, `rgba(${Math.round(card.bkgd_colour[0])},${Math.round(card.bkgd_colour[1])},${Math.round(card.bkgd_colour[2])}, 255)`);
  const hasSprite = cardCache[card.template_id];

  const renderSprite = () => {
    if (!hasSprite) return null;
    const { image, isMini } = cardCache[card.template_id];
    if (!isMini) {
      return <img class="hc-sprite" src={image.src} alt=""/>;
    } else {
      return <img class="hc-mini-sprite" src={image.src} alt=""/>;
    }
  };

  return (
    <div class="hc-card"
      style={{backgroundColor: hasSprite? `${bkgd_colour}` : "lightgrey"}}
      onMouseOver={enterHover} onMouseLeave={leaveHover}
    >
      <h2 class="hc-title" >{card.name}</h2>
      <h4 class="hc-description" style={{backgroundColor: `${colour}`}}>{card.description}</h4>
      {hasSprite && renderSprite()}
      <i class="hc-flavour">{card.flavour}</i>
      <h4 class="hc-attack">{card.attack}</h4>
      <h4 class="hc-health">{card.health}</h4>
      <h4 class="hc-cost">{card.cost}</h4>
    </div>
  );
}

