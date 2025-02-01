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

type Card = string;

type Action = {
    type: string;
    
    amount?: number;
    amountToCall?: number;
}

type GameTurn = {
    player: Player;
    actions: Action[];
}

type Winner = {
    players: Player[];
    hand?: Card[];
    rank?: string;
};

// export all
export type { Player, Game, Pot, Card, Action, GameTurn, Winner };