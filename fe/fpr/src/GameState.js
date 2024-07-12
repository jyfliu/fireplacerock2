// helper functions for resolving game state


export function CanSummon(state) {
  let { phase, hasInitiative, ownerStats } = state;
  return (card) => {
    return hasInitiative && phase[1].includes("main") && ownerStats.mana >= card.cost && card.can_summon;
  }
};

export function CanActivateHand(state) {
  let { phase, hasInitiative, ownerStats } = state;
  return (card) => {
    return hasInitiative && phase[1].includes("main") && ownerStats.mana >= card.cost && card.can_activate_hand;
  }
};

export function CanAttack(state) {
  let { phase, hasInitiative } = state;
  return (card) => {
    return hasInitiative && phase === "battle" && card.can_attack;
  }
};

