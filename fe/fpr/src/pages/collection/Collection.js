import { useEffect, useState } from "react";
import { socket } from '../../socket';
import { unserializeTemplate } from './CollectionUtils'
import { Card } from "../../components/CollectionComponents/CollectionCard";

import './Collection.css';

export default function Collection() {
  const [cardArray, setCardArray] = useState(null)
  useEffect(() => {
    socket.emit("collection", "wilson", (response) => {
      const res = response.map(unserializeTemplate)
      res.splice(res.length - 20, 20);
      setCardArray(res)
    });
  }, []);


  const mainPanel = <>
    <div className="cardsDisplay">
      {cardArray === null ? <div>'loading'</div> : cardArray.map((card) =>
        <Card card={card} />

      )
      }
    </div>

  </>

  return (
    <>
      {mainPanel}
    </>
  );
}