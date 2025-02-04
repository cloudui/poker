<script lang="ts">
  import { startGame } from "$lib/poker";
  import { onMount } from "svelte";
  import type {Player, Game, Pot, GameTurn, Action, Winner } from "$lib/types";
  import Card from "$lib/components/Card.svelte";

  let gameStarted = false;
  let players: Player[] = [];
  let gameStage = "";
  let pot: Pot;
  let smallBlindPlayer: string;
  let bigBlindPlayer: string;
  let turn: GameTurn | null = null;
  let communityCards: string[] = [];

  let enableBet = false;
  let enableRaise = false;
  let enableFold = false;
  let enableCheck = false;
  let enableCall = false;

  let betAction: Action | null = null;
  let raiseAction: Action | null = null;
  let foldAction: Action | null = null;
  let checkAction: Action | null = null;
  let callAction: Action | null = null;

  let playerAction: Action = {
    type: "",
    amount: 0,
    amountToCall: 0
  }
  let playerActionAmount = "";

  let winner: Winner | null = null;

  async function handleStartGame() {
    try {
      const response = await fetch('http://localhost:5000/start_game');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      console.log(data);
      players = data.players;
      gameStage = data.stage;
      gameStarted = true;
      pot = data.pot;
      smallBlindPlayer = data.small_blind_player;
      bigBlindPlayer = data.big_blind_player;
      turn = data.turn;
      communityCards = data.community_cards;
      parseActions(turn!.actions);
    } catch (error) {
      console.error('Fetch error:', error);
    }
  }

  async function nextRound() {
    try {
      const response = await fetch('http://localhost:5000/next_round', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
      });
      const data = await response.json();
      console.log(data);
      communityCards = data.community_cards;
      players = data.players;
      gameStage = data.stage;
      gameStarted = true;
      pot = data.pot;
      smallBlindPlayer = data.small_blind_player;
      bigBlindPlayer = data.big_blind_player;
      turn = data.turn;
      clearActions();
      parseActions(turn!.actions);
    } catch (error) {
      console.error('Fetch error:', error);
    }
  }

  function playerCheck() {
    playerAction.type = "check";
    handlePlayerTurn();
  }

  function playerBet() {
    playerAction.type = "bet";
    playerAction.amount = parseInt(playerActionAmount);
    handlePlayerTurn();
  }

  function playerCall() {
    playerAction.type = "call";
    handlePlayerTurn();
  }

  function playerRaise() {
    playerAction.type = "raise";
    playerAction.amount =parseInt(playerActionAmount);
    handlePlayerTurn();
  }

  function playerFold() {
    playerAction.type = "fold";
    handlePlayerTurn();
  }
  
  async function handlePlayerTurn() {
    try {
      const response = await fetch('http://localhost:5000/next_turn', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          player_name: turn.player.name,
          action: playerAction
        })
      });
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      console.log(data);
      communityCards = data.community_cards;
      players = data.players;
      gameStage = data.stage;
      pot = data.pot;
      turn = data.turn;
      clearActions();
      parseActions(turn!.actions);
      winner = data.winner;
    } catch (error) {
      console.error('Fetch error:', error);
    }
  }

  function parseActions(actions: Action[]) {
    for (const action of actions) {
      switch (action.type.toLowerCase()) {
        case "bet":
          betAction = parseAction(action);
          enableBet = true;
          break;
        case "raise":
          raiseAction = parseAction(action);
          enableRaise = true;
          break;
        case "fold":
          foldAction = parseAction(action);
          enableFold = true;
          break;
        case "check":
          checkAction = parseAction(action);
          enableCheck = true;
          break;
        case "call":
          callAction = parseAction(action);
          enableCall = true;
          break;
        default:
          break;
    }
  }
}

function parseAction(action: any): Action {
  return {
    type: action.type,
    amount: action.amount,
    amountToCall: action.amountToCall
  }
}

function clearActions() {
  playerActionAmount = "";

  enableBet = false;
  enableRaise = false;
  enableFold = false;
  enableCheck = false;
  enableCall = false;
}

function actionString(action: Action) {
  if (action.allIn) {
    return `ALL-IN ${action.amount}`;
  } else if (action.type === "CALL") {
    return `CALL ${action.amountToCall}`;
  } else if (action.type === "BET") {
    return `BET ${action.amount}`;
  } else if (action.type === "RAISE") {
    return `RAISE ${action.amount}`;
  } else if (action.type === "FOLD") {
    return "FOLD";
  } else if (action.type === "CHECK") {
    return "CHECK";
  } else if (action.type === "SMALL_BLIND") {
    return "SMALL BLIND";
  } else if (action.type === "BIG_BLIND") {
    return "BIG BLIND";
  }

  return "ERROR";

}

</script>

<div class="page max-w-4xl mx-auto pt-8">
  <h1 class="text-3xl font-bold mb-4">Poker Game</h1>

  <!-- blue button -->
  {#if !gameStarted}
  <button type="button" class="btn" on:click={handleStartGame}> Start Game </button>
  {/if}

  {#if gameStarted}
  <section class="flex items-center flex-col gap-2">
    <h2 class="text-2xl font-bold text-center">{gameStage}</h2>
    <div class="stats shadow">
      <div class="stat place-items-center">
        <div class="stat-title">Current pot</div>
        <div class="stat-value">${pot.amount}</div>
      </div>
    </div>
    <div class="flex gap-4 mt-3 mb-3">
      {#each communityCards as card (card)}
        <Card card={card} />
      {/each}
    </div>
  </section>

  {#if gameStage === "ROUND_OVER"}
    <div class="flex flex-col items-center gap-5">
      <button type="button" class="btn btn-accent" on:click={nextRound}> Next Round </button>
    </div>
  {/if}

  <div class="container mx-auto py-6">
    {#if winner}
      <div class="modal" open>
        <div class="modal-box">
          <h3 class="text-lg font-bold">Winner</h3>
          {#each winner.players as player}
            <p class="text-primary mb-2">{player.name}</p>
          {/each}  
          {#if winner.hand}
          <div class="flex flex-row gap-2 mb-2">
              {#each winner.hand as card (card)}
                <Card card={card} />
              {/each}
          </div>
          {/if}
          <p class="mb-10">{winner.rank}</p>
        
          <div class="modal-action">
            <button class="btn" on:click={winner = null}>Close</button>
          </div>
        </div>
      </div>
    {/if}


    {#if turn}
    <h2 class="text-2xl font-bold text-center mb-2">Player Turn: {turn.player.name}</h2>

    
    <div class="card shadow-lg bg-base-100">
      <div class="card-body flex flex-col sm:flex-row items-center justify-between">
        <!-- User Info -->
        <div class="flex items-center gap-4">
          <div class="avatar">
            <div class="w-12 rounded-full ring ring-primary ring-offset-base-100 ring-offset-2">
              <img src="https://api.dicebear.com/6.x/bottts/svg?seed={turn.player.name}" alt="{turn.player.name}" />
            </div>
          </div>
          <div>
            <h2 class="card-title">{turn.player.name}</h2>
            <p class="text-sm text-gray-500">Stack: ${turn.player.stack}</p>
            
          </div>
        </div>

        <!-- Cards -->
        <div class="flex gap-2 mt-4 sm:mt-0">
          {#each turn.player.hand as card (card)}
            <Card card={card} />
          {/each}
        </div>
      </div>
    </div>
    {/if}

    <!-- Action List (centered buttons) -->
    <div class="flex flex-col items-center gap-5">
      <div class="flex flex-row gap-4 mt-4 justify-center">
        <button type="button" class="btn btn-neutral" disabled={!enableBet} on:click={playerBet}> Bet (min ${betAction ? betAction.amount : ''}) </button>
        <button type="button" class="btn" disabled={!enableCall} on:click={playerCall}> 
          Call (${callAction ? callAction.amountToCall : ''}) 
        </button>
        <button type="button" class="btn btn-primary" disabled={!enableRaise} on:click={playerRaise}> 
          Raise (${raiseAction ? raiseAction.amount : ''}) 
        </button>
        <button type="button" class="btn btn-secondary" disabled={!enableFold} on:click={playerFold}> Fold </button>
        <button type="button" class="btn btn-accent" disabled={!enableCheck} on:click={playerCheck}> Check </button>
      </div>
      <input type="text" placeholder="Bet Amount" class="input input-bordered input-accent max-w-xs" bind:value={playerActionAmount} />
    </div>
               

  </div>

  <div class="container mx-auto py-6">
    <h2 class="text-2xl font-bold text-center mb-2">Players</h2>
    <div class="grid gap-4">
      {#each players as user (user.name)}
        <div class="card shadow-lg bg-base-100">
          <div class="card-body flex flex-col sm:flex-row items-center justify-between">
            <!-- User Info -->
            <div class="flex items-center gap-4">
              <div class="avatar">
                <div class="w-12 rounded-full ring ring-primary ring-offset-base-100 ring-offset-2">
                  <img src="https://api.dicebear.com/6.x/bottts/svg?seed={user.name}" alt="{user.name}" />
                </div>
              </div>
              <div>
                <h2 class="card-title">{user.name}</h2>
                <p class="text-sm text-gray-500">Stack: ${user.stack}</p>
                {#if user.action }
                  <p class="text-sm text-accent">{actionString(user.action)}</p>
                {/if}
              </div>
            </div>
  
            <!-- Cards -->
            <div class="flex gap-2 mt-4 sm:mt-0">
              {#each user.hand as card (card)}
                <Card card={card} />
              {/each}
            </div>
          </div>
        </div>
      {/each}
    </div>
  </div>
  {/if}

</div>

