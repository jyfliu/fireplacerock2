import React from 'react';

import './PlayerStats.css';


export function PlayerStats(props) {
  const { owner, hp } = props;


  return (
    <div class={owner? "owner-player-stats-border" : "oppon-player-stats-border"}>
      <p class={owner? "owner-player-stats" : "oppon-player-stats"} >
        {hp} LP
      </p>
    </div>
  );
}

export function PlayerMana(props) {
  const { owner, mana, manaMax } = props;


  return (
    <div class={owner? "owner-player-mana-border" : "oppon-player-mana-border"}>
      <p class={owner? "owner-player-mana" : "oppon-player-mana"} >
        {mana} / {manaMax} Mana
      </p>
    </div>
  );
}
