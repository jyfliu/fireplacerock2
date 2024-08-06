import { useHistory } from "react-router-dom";
import { ROUTES } from "../RouterUtils";

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

    return (<div>
        <button onClick={gameOnClick}>
            Game
        </button>
        <button onClick={collectionOnClick}>
            Collection
        </button>
    </div>);
}