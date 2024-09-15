import { useEffect } from "react";
import { socket } from '../socket';

export default function Collection(){
    useEffect(() => {
        socket.emit("collection", "wilson")
    })

    const mainPanel = <div> mp </div>
    return (
    <>
    {mainPanel}
    <div>collection</div>
    </>
    );
}