import { useHistory } from "react-router-dom";
import useCookie from 'react-use-cookie';
import { ROUTES } from "../RouterUtils";
import { socket } from '../socket';

import './Home.css';

export default function Home() {
  const history = useHistory();

  const [username, setUsername, removeUsername] = useCookie("username", "");
  const [, setPassphrase, removePassphrase] = useCookie("passphrase", "");

  const loginOnClick = () => {
    let user = prompt("What is your username");
    socket.emit("login", user, "", (result) => {
      let password = "";

      if (result === "wrong_username") {
        password = prompt("What is your favorite food? This will be used as your password. DO NOT USE A REAL PASSWORD.");
        socket.emit("new_user", user, password, (success) => {
          if (success) {
            setUsername(user);
            setPassphrase(password);
          } else {
            alert("Account creation failed (?)");
          }
        });
      } else if (result === "wrong_password") {
        password = prompt("What is your favorite food? If you forgot, message Jeffrey.");
        setUsername(user);
        setPassphrase(password);
      } else {
        alert("Log in failed (?)");
      }
    });
  };

  const logoutOnClick = () => {
    let logout = window.confirm("Log out?");
    if (logout) {
      removeUsername();
      removePassphrase();
    }
  };

  const checkFail = () => {
    if (!username) {
      alert("You must be logged in.");
      return true;
    }
    return false;
  };

  const playOnClick = () => {
    if (checkFail()) return;
    history.push(ROUTES.GAME);
    console.log(history);
  }
  const collectionOnClick = () => {
    if (checkFail()) return;
    history.push(ROUTES.COLLECTION);
    console.log(history);
  }
  const gachaOnClick = () => {
    if (checkFail()) return;
    history.push(ROUTES.GACHA);
    console.log(history);
  }

  return (
    <>
      <div className="buttonGroup">
        <div className="title">
          <b>
              Fireplace Rock
          </b>
        </div>
        <button onClick={playOnClick} className="button">
          Play!
        </button>
        <button onClick={collectionOnClick} className="button">
          Collection
        </button>
        <button onClick={gachaOnClick} className="button">
          Open New Packs
        </button>
      </div>
      <button class="login" onClick={username? logoutOnClick : loginOnClick} >
        {username? username : "Log in"}
      </button>
    </>
  );
}
