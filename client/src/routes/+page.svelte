<script lang="ts">
  import { onMount } from "svelte";
  import {
    gameState,
    connectWebSocket,
    sendPlayerAction,
    connectionStatus,
    startGame,
  } from "$lib/stores/gameStore";
  import Card from "$lib/components/Card.svelte";
  import { actionString } from "$lib/gameUtils";
  import type { Action } from "$lib/types";

  let playerName = "Tyson the Conqueror"; // Change dynamically in real app

  // actions
  let enableBet = false;
  let enableRaise = false;
  let enableFold = false;
  let enableCheck = false;
  let enableCall = false;

  let betAction: Action | null = {
    type: "bet",
    amount: 0,
  };
  let raiseAction: Action | null = {
    type: "raise",
    amount: 0,
  }
  let foldAction: Action | null = null;
  let checkAction: Action | null = null;
  let callAction: Action | null = {
    type: "call",
    amountToCall: 69,
  };
  let playerActionAmount = "";

  // Connect WebSocket on component mount
  onMount(() => {
    connectWebSocket(playerName);
  });

  // Function to send player action (example)
  function handleAction(actionType: string) {
    sendPlayerAction(playerName, { type: actionType });
    playerActionAmount = "";
  }
</script>

<main>

  <div class="page max-w-4xl mx-auto pt-8">
    <h1 class="text-3xl font-bold mb-1">Poker Game</h1>
    <div class="mb-3">
      {#if $connectionStatus === "connected"}
        <div class="badge badge-success">connected</div>
      {:else if $connectionStatus === "disconnected"}
        <div class="badge badge-error">disconnected</div>
      {:else}
        <div class="badge badge-warning">connecting...</div>
      {/if}
    </div>

    {#if !$gameState}
      <button type="button" class="btn" on:click={startGame}>
        Start Game
      </button>
    {/if}

    {#if $gameState}
      <section class="flex items-center flex-col gap-2">
        <h2 class="text-2xl font-bold text-center">{$gameState.stage}</h2>
        <div class="stats shadow">
          <div class="stat place-items-center">
            <div class="stat-title">Current pot</div>
            <div class="stat-value">${$gameState.pot.amount}</div>
          </div>
        </div>
        <div class="flex gap-4 mt-3 mb-3">
          {#each $gameState.community_cards as card (card)}
            <Card {card} />
          {/each}
        </div>
      </section>

      <!-- {#if gameStage === "ROUND_OVER"}
        <div class="flex flex-col items-center gap-5">
          <button type="button" class="btn btn-accent" on:click={nextRound}>
            Next Round
          </button>
        </div>
      {/if} -->

      <div class="container mx-auto py-6">
        {#if $gameState.winner}
          <dialog class="modal" open>
            <div class="modal-box">
              <h3 class="text-lg font-bold">Winner</h3>
              {#each $gameState.winner.players as player}
                <p class="text-primary mb-2">{player.name}</p>
              {/each}
              {#if $gameState.winner.hand}
                <div class="flex flex-row gap-2 mb-2">
                  {#each $gameState.winner.hand as card (card)}
                    <Card {card} />
                  {/each}
                </div>
              {/if}
              <p class="mb-10">{$gameState.winner.rank}</p>

              <div class="modal-action">
                <button class="btn" on:click={($gameState.winner = undefined)}>Close</button>
              </div>
            </div>
          </dialog>
        {/if}

        {#if $gameState.turn}
          <h2 class="text-2xl font-bold text-center mb-2">
            Player Turn: {$gameState.turn.player.name}
          </h2>

          <div class="card shadow-lg bg-base-100">
            <div
              class="card-body flex flex-col sm:flex-row items-center justify-between"
            >
              <!-- User Info -->
              <div class="flex items-center gap-4">
                <div class="avatar">
                  <div
                    class="w-12 rounded-full ring ring-primary ring-offset-base-100 ring-offset-2"
                  >
                    <img
                      src="https://api.dicebear.com/6.x/bottts/svg?seed={$gameState.turn
                        .player.name}"
                      alt={$gameState.turn.player.name}
                    />
                  </div>
                </div>
                <div>
                  <h2 class="card-title">{$gameState.turn.player.name}</h2>
                  <p class="text-sm text-gray-500">Stack: ${$gameState.turn.player.stack}</p>
                </div>
              </div>

              <!-- Cards -->
              <div class="flex gap-2 mt-4 sm:mt-0">
                {#each $gameState.turn.player.hand as card (card)}
                  <Card {card} />
                {/each}
              </div>
            </div>
          </div>
        {/if}

        <!-- Action List (centered buttons) -->
        <div class="flex flex-col items-center gap-5">
          <div class="flex flex-row gap-4 mt-4 justify-center">
            <button
              type="button"
              class="btn btn-neutral"
              disabled={!enableBet}
              on:click={() => handleAction("bet")}
            >
              Bet (min ${betAction ? betAction.amount : ""})
            </button>
            <button
              type="button"
              class="btn"
              disabled={!enableCall}
              on:click={() => handleAction("call")}
            >
              Call (${callAction ? callAction.amountToCall : ""})
            </button>
            <button
              type="button"
              class="btn btn-primary"
              disabled={!enableRaise}
              on:click={() => handleAction("raise")}
            >
              Raise (${raiseAction ? raiseAction.amount : ""})
            </button>
            <button
              type="button"
              class="btn btn-secondary"
              disabled={!enableFold}
              on:click={() => handleAction("fold")}
            >
              Fold
            </button>
            <button
              type="button"
              class="btn btn-accent"
              disabled={!enableCheck}
              on:click={() => handleAction("check")}
            >
              Check
            </button>
          </div>
          <input
            type="text"
            placeholder="Bet Amount"
            class="input input-bordered input-accent max-w-xs"
            bind:value={playerActionAmount}
          />
        </div>
      </div>

      <div class="container mx-auto py-6">
        <h2 class="text-2xl font-bold text-center mb-2">Players</h2>
        <div class="grid gap-4">
          {#each $gameState.players as user (user.name)}
            <div class="card shadow-lg bg-base-100">
              <div
                class="card-body flex flex-col sm:flex-row items-center justify-between"
              >
                <!-- User Info -->
                <div class="flex items-center gap-4">
                  <div class="avatar">
                    <div
                      class="w-12 rounded-full ring ring-primary ring-offset-base-100 ring-offset-2"
                    >
                      <img
                        src="https://api.dicebear.com/6.x/bottts/svg?seed={user.name}"
                        alt={user.name}
                      />
                    </div>
                  </div>
                  <div>
                    <h2 class="card-title">{user.name}</h2>
                    <p class="text-sm text-gray-500">Stack: ${user.stack}</p>
                    {#if user.action}
                      <p class="text-sm text-accent">
                        {actionString(user.action)}
                      </p>
                    {/if}
                  </div>
                </div>

                <!-- Cards -->
                <div class="flex gap-2 mt-4 sm:mt-0">
                  {#each user.hand as card (card)}
                    <Card {card} />
                  {/each}
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>

</main>

