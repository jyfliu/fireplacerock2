import { useEffect, useState } from "react";

import './CollectionDeckDisplay.css';
import DeckListItem from "./DeckListItem";

export default function CollectionDeckDisplay(props) {
  const { deck, removeFromDeck } = props;
  let deckArr = []

  for (var key in deck) {
    if (deck.hasOwnProperty(key)) {
      deckArr.push([key, deck[key]]);
    }
  }

  deckArr.sort(function (a, b) {
    if (a.cost == b.cost) {
      return a.name > (b.name) ? 1 : -1;
    }
    return a.cost > b.cost ? 1 : -1;;
  });


  return (<div>
    {deckArr.map((item) => {
      return <DeckListItem count={item[1][0]} card={item[1][1]} removeFromDeck={removeFromDeck} />
    }
    )}
  </div>)
}