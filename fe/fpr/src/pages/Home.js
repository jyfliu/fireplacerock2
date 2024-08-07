import { useHistory } from "react-router-dom";
import { ROUTES } from "../RouterUtils";
import {View} from 'react';

import './Home.css';

export default function Home(){
    const history = useHistory();
    const gameOnClick = () => {
        history.push(ROUTES.GAME);
        console.log(history)
    }
    const collectionOnClick = () => {
        history.push(ROUTES.COLLECTION);
        console.log(history)
    }

    return (
        <div className="buttonGroup">
            <div className="title">
                <b>
                    Fireplace Rock
                </b>
            </div>
            <button onClick={gameOnClick} className="button">
                Game
            </button>
            <button onClick={collectionOnClick} className="button">
                Collection
            </button>
        </div>
);
}