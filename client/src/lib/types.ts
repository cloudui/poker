type Player = {
  name: string;
  stack: number;
  hand: string[];
};

type Game = {
  players: Player[];
  stage: string;
};

export type { Player, Game };