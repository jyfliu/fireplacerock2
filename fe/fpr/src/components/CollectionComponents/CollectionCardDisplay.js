import { useState } from "react";
import { Card } from "../../components/CollectionComponents/CollectionCard";

import './CollectionCardDisplay.css';

export default function CollectionCardDisplay(props) {
  const { cardArray } = props
  const [page, setPage] = useState(0)

  cardArray.sort(function (a, b) {
    if (a.cost == b.cost) {
      return a.name > (b.name) ? 1 : -1;
    }

    return a.cost > b.cost ? 1 : -1;;
  });

  const filteredCards = cardArray.filter((card) => card.cost >= 0)
  const maxPage = filteredCards.length / 8
  const shownCards = filteredCards.slice(page * 8, page * 8 + 8)


  const handleNext = () => {
    setPage(page + 1)
  }
  const handleBack = () => {
    console.log('back clicked')
    setPage(page - 1)
  }

  return (
    <div className="mainContainer">
      <button disabled={page <= 0} className={'pageButtonLeft'} onClick={handleBack}>back</button>
      <div className="cardsDisplay">
        {shownCards.map((card) =>
          <Card card={card} />
        )}
      </div>
      <button disabled={page > maxPage} className={'pageButtonRight'} onClick={handleNext}>next</button>
    </div>);
}