<script>
  import { onMount } from "svelte";
  import { io } from "socket.io-client";

  let socket;
  let roomId = "";
  let playerName = "";
  let stack = 100;
  let gameState = null;
  let action = "";
  let actionAmount = 0;

  onMount(() => {
    socket = io("http://127.0.0.1:5000"); // Flask server address

    // Listen for game updates
    socket.on("game_update", (data) => {
      gameState = data;
    });

    // Handle errors
    socket.on("error", (data) => {
      alert(data.error || "An error occurred");
    });
  });

  function joinGame() {
    fetch("http://127.0.0.1:5000/join_game", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ room_id: roomId, player_name: playerName, stack }),
    })
      .then((res) => res.json())
      .then((data) => alert(data.message || "Joined the game!"))
      .catch((err) => alert("Error joining game: " + err.message));
  }

  function startRound() {
    socket.emit("start_round", { room_id: roomId });
  }

  function sendAction() {
    if (!action) return alert("Please select an action.");
    socket.emit("player_action", {
      room_id: roomId,
      player_id: playerName, // Using name as a simple ID
      action,
      amount: actionAmount,
    });
    action = "";
    actionAmount = 0;
  }
</script>

<div class="max-w-4xl mx-auto mt-8">
  <h1 class="text-3xl font-bold mb-4">Poker Game</h1>
  
  <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
    Join Game
  </button>

</div>