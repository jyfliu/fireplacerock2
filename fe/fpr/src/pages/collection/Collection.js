import { useEffect } from "react";
import { socket } from '../../socket';
import unserializeTemplate from './CollectionUtils'

export default function Collection() {
  let cardArray = null
  useEffect(() => {
    socket.emit("collection", "wilson", (response) => {
      cardArray = response.map((template) => unserializeTemplate(template))
    });
  })

  const mainPanel = <>

  </>

  return (
    <>
      {mainPanel}
      <div>collection</div>
    </>
  );
}