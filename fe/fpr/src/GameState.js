// helper functions for resolving game state


export function CanSummon(state) {
  let { phase, hasInitiative, ownerStats } = state;
  return (card) => {
    return hasInitiative && phase.includes("main") && ownerStats.mana >= card.cost && card.can_summon;
  }
};

