import React from 'react';

import './CollectionCard.css';
import { pSBC } from '../../Utils.js';
import { vmin, inches } from '../../Utils.js';

export function Card(props) {
  const { card, addToDeck } = props;
  if (!card || !card.name) {
    return <div>error</div>;
  }

  const handleAddClick = () => {
    addToDeck(card)
  }

  const hasSprite = card.spriteImg != null
  const colour = pSBC(0.50, `rgba(${Math.round(card.bkgd_colour[0])},${Math.round(card.bkgd_colour[1])},${Math.round(card.bkgd_colour[2])}, 0.8)`);
  const bkgd_colour = pSBC(0.2, `rgba(${Math.round(card.bkgd_colour[0])},${Math.round(card.bkgd_colour[1])},${Math.round(card.bkgd_colour[2])}, 255)`);

  const renderSprite = () => {
    if (!card.spriteImg) return null;
    const image = card.spriteImg
    const isMini = card.isMini
    if (!isMini) {
      return <img class="cc-sprite" src={image.src} alt="" />;
    } else {
      return <img class="cc-mini-sprite" src={image.src} alt="" />;
    }
  };

  return (
    <div
      class="cc-cardWrapper"
      key={card.name + '_card'}
      style={{
        zoom: vmin(25.5) / inches(9.6),
        transformOrigin: "top left"
      }}>

      <button
        class='cardButton'
        onClick={handleAddClick}>
        <div class="cc-card"
          style={{
            backgroundColor: hasSprite ? `${bkgd_colour}` : "lightgrey",
          }}
        >
          <h2 class="cc-title" >{card.name}</h2>
          <h4 class="cc-description" style={{ backgroundColor: `${colour}` }}>{card.description}</h4>
          {hasSprite && renderSprite()}
          {/* <i class="cc-flavour">{card.flavour}</i> */}
          {card.type.includes("monster") &&
            <>
              <h4 class="cc-attack">{card.attack}</h4>
              <h4 class="cc-health">{card.health}</h4>
            </>
          }
          <h4 class="cc-cost">{card.cost}</h4>
        </div>

      </button>
    </div>
  );
}

