import { useEffect, useState } from "react";
import { socket } from '../../socket';
import { unserializeTemplate } from './CollectionUtils'

import './Collection.css';
import CollectionCardDisplay from "../../components/CollectionComponents/CollectionCardDisplay";

export default function Collection() {
  const [cardArray, setCardArray] = useState(null)
  useEffect(() => {
    socket.emit("collection", "wilson", (response) => {
      const res = response.map(unserializeTemplate)
      setCardArray(res)
    });
  }, []);

  const mainPanel = <>
    {cardArray === null ? <div>'loading'</div> : <CollectionCardDisplay cardArray={cardArray} />}
  </>

  return (
    <>
      {mainPanel}
    </>
  );
}