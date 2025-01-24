<script>
    import { onMount } from 'svelte';
    import { io } from 'socket.io-client';
  
    let socket;
    let roomId = '';
    let playerName = '';
    let stack = 100;
    let gameState = null;
    let action = '';
    let actionAmount = 0;
  
    onMount(() => {
      socket = io('http://127.0.0.1:5000'); // Flask server address
  
      // Listen for game updates
      socket.on('game_update', (data) => {
        gameState = data;
      });
  
      // Handle errors
      socket.on('error', (data) => {
        alert(data.error || 'An error occurred');
      });
    });
  
    function joinGame() {
      fetch('http://127.0.0.1:5000/join_game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ room_id: roomId, player_name: playerName, stack })
      })
        .then((res) => res.json())
        .then((data) => alert(data.message || 'Joined the game!'))
        .catch((err) => alert('Error joining game: ' + err.message));
    }
  
    function startRound() {
      socket.emit('start_round', { room_id: roomId });
    }
  
    function sendAction() {
      if (!action) return alert('Please select an action.');
      socket.emit('player_action', {
        room_id: roomId,
        player_id: playerName, // Using name as a simple ID
        action,
        amount: actionAmount
      });
      action = '';
      actionAmount = 0;
    }
  </script>
  
  <style>
    .container {
      max-width: 800px;
      margin: 0 auto;
      padding: 2rem;
    }
  
    .actions {
      margin-top: 1rem;
    }
  
    pre {
      background: #f4f4f4;
      padding: 1rem;
      border-radius: 5px;
      overflow-x: auto;
    }
  </style>
  
  <div class="container">
    <h1>Poker Game</h1>
  
    <div>
      <h2>Join a Game</h2>
      <input bind:value={roomId} placeholder="Room ID" />
      <input bind:value={playerName} placeholder="Your Name" />
      <input type="number" bind:value={stack} placeholder="Stack" />
      <button on:click={joinGame}>Join Game</button>
    </div>
  
    <div>
      <h2>Game Controls</h2>
      <button on:click={startRound}>Start Round</button>
    </div>
  
    <div>
      <h2>Send Action</h2>
      <select bind:value={action}>
        <option value="" disabled selected>Select Action</option>
        <option value="bet">Bet</option>
        <option value="fold">Fold</option>
        <option value="call">Call</option>
        <option value="raise">Raise</option>
        <option value="check">Check</option>
      </select>
      <input type="number" bind:value={actionAmount} placeholder="Amount (if applicable)" />
      <button on:click={sendAction}>Send Action</button>
    </div>
  
    <div>
      <h2>Game State</h2>
      {#if gameState}
        <pre>{JSON.stringify(gameState, null, 2)}</pre>
      {/if}
    </div>
  </div>