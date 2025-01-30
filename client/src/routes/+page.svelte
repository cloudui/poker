<script lang="ts">
  import { startGame } from "$lib/poker";
  import { onMount } from "svelte";
  import type {Player, Game, Pot, GameTurn, Action } from "$lib/types";
  import Card from "$lib/components/Card.svelte";

  let gameStarted = false;
  let players: Player[] = [];
  let gameStage = "";
  let pot: Pot;
  let smallBlindPlayer: string;
  let bigBlindPlayer: string;
  let turn: GameTurn;

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
      parseActions(turn.actions);
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

  function parseAction(action: any): Action {
    return {
      type: action.type,
      amount: action.amount,
      amountToCall: action.amount_called
    }
  }
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
        <div class="stat-desc">Current Round Pot</div>
      </div>
    </div>
  </section>

  <div class="container mx-auto py-6">
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

    <!-- Action List (centered buttons) -->
    <div class="flex flex-row gap-4 mt-4 justify-center">
      <button type="button" class="btn btn-neutral" disabled={!enableBet}> Bet (min ${betAction ? betAction.amount : ''}) </button>
      <button type="button" class="btn" disabled={!enableCall}> Call (${callAction ? callAction.amountToCall : ''}) </button>
      <button type="button" class="btn btn-primary" disabled={!enableRaise}> Raise </button>
      <button type="button" class="btn btn-secondary" disabled={!enableFold}> Fold </button>
      <button type="button" class="btn btn-accent" disabled={!enableCheck}> Check </button>

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
                {#if user.name === smallBlindPlayer}
                  <p class="text-sm text-gray-500 font-bold">Small Blind</p>
                {/if}
                {#if user.name === bigBlindPlayer}
                  <p class="text-sm text-gray-500 font-bold">Big Blind</p>
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

