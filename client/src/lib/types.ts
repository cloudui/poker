type Player = {
  name: string;
  stack: number;
  hand: string[];
  action?: Action;
};

type Game = {
  players: Player[];
  stage: string;
};

type Pot = {
    amount: number;
}

type Action = {
    type: string;
    
    amount?: number;
    amountToCall?: number;
}


type GameTurn = {
    player: Player;
    actions: Action[];
}

// export all
export type { Player, Game, Pot, GameTurn, Action };