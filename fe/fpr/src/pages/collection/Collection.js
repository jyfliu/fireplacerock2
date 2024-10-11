import { useEffect, useState } from "react";
import { socket } from '../../socket';
import { unserializeTemplate } from './CollectionUtils'

import './Collection.css';
import CollectionCardDisplay from "../../components/CollectionComponents/CollectionCardDisplay";
import CollectionDeckDisplay from "../../components/CollectionComponents/CollectionDeckDisplay";

export default function Collection() {
  const [cardArray, setCardArray] = useState(null)
  const [deckSize, setDeckSize] = useState(0)
  const [deck, setDeck] = useState([])

  const addToDeck = (card) => {
    if (deckSize < 40) {
      if (deck[card.name] == null) {
        deck[card.name] = [1, card];
        setDeckSize(deckSize + 1)
      } else if (deck[card.name][0] < 4) {
        deck[card.name] = [deck[card.name][0] + 1, card]
        setDeckSize(deckSize + 1)
      }
    }
    console.log(deck)
  }

  const removeFromDeck = (card) => {
    if (deck[card.name] != null) {
      if (deck[card.name][0] == 1) {
        delete deck[card.name]
      } else {
        deck[card.name] = [deck[card.name][0] - 1, card]
      }
    }
    setDeckSize(deckSize + 1)
    console.log(deck)
  }

  useEffect(() => {
    socket.emit("collection", "wilson", (response) => {
      const res = response.map(unserializeTemplate)
      setCardArray(res)
    });
  }, []);

  const mainPanel = <>
    {cardArray === null ? <div>'loading'</div> : <CollectionCardDisplay addToDeck={addToDeck} cardArray={cardArray} />}
  </>

  // TODO: get deck from server side if not in new deck & pass into display
  const rightPanel = <>
    {true === false ? <div>'deck loading'</div> : <CollectionDeckDisplay deck={deck} removeFromDeck={removeFromDeck} />}
  </>

  return (
    <>
      <div>
        {mainPanel}
      </div>
      <div>
        {rightPanel}
      </div>

    </>
  );
}