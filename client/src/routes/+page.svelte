<script lang="ts">
  import { startGame } from "$lib/poker";
  import { onMount } from "svelte";
  import type {Player, Game} from "$lib/types";
  import Card from "$lib/components/Card.svelte";

  let gameStarted = false;
  let players: Player[] = [];
  let gameStage = "";

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
    } catch (error) {
      console.error('Fetch error:', error);
    }
  }
</script>

<div class="page max-w-4xl mx-auto pt-8">
  <h1 class="text-3xl font-bold mb-4">Poker Game</h1>

  <!-- blue button -->
  <button type="button" class="btn variant-filled" on:click={handleStartGame}> Start Game </button>

  <p>Game Stage: {gameStage}</p>
  <div class="stats shadow">
    <div class="stat">
      <div class="stat-title">Total Page Views</div>
      <div class="stat-value">89,400</div>
      <div class="stat-desc">21% more than last month</div>
    </div>
  </div>

  <h2>Players</h2>

  <div class="container mx-auto py-6">
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

</div>

