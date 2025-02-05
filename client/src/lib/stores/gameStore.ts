import { writable } from "svelte/store";
import type {
  Player,
  Game,
  Pot,
  Card,
  Action,
  GameTurn,
  Winner,
} from "$lib/types";

// Define TypeScript types for game state and WebSocket connection
export interface GameState {
  players: Player[];
  stage: string;
  community_cards: Card[];
  turn: GameTurn;
  pot: Pot;
  winner?: Winner;
}

export const gameState = writable<GameState | null>(null);
export const connectionStatus = writable<
  "connected" | "disconnected" | "error"
>("disconnected");

let socket: WebSocket | null = null;

export async function startGame() {
  try {
      const res = await fetch("http://localhost:8000/start_game", {
          method: "POST",
      });
      if (!res.ok) {
          throw new Error("Failed to start game");
      }
      const data = await res.json();
      gameState.set(data);
  } catch (error) {
      console.error("Error starting game:", error);
  }
}

/**
 * Connects a player to the WebSocket server.
 * @param playerName - Name of the player connecting.
 */
export function connectWebSocket(playerName: string): void {
  if (socket) {
    socket.close(); // Close existing connection before reconnecting
  }

  socket = new WebSocket(`ws://localhost:8000/ws/${playerName}`);

  socket.onopen = () => {
    console.log("Connected to WebSocket");
    connectionStatus.set("connected");
  };

  socket.onmessage = (event: MessageEvent) => {
    try {
      const data: GameState = JSON.parse(event.data);
      console.log("Game update:", data);
      gameState.set(data);
    } catch (error) {
      console.error("Failed to parse WebSocket message:", error);
    }
  };

  socket.onclose = () => {
    console.log("Disconnected from WebSocket");
    connectionStatus.set("disconnected");
  };

  socket.onerror = (error) => {
    console.error("WebSocket error:", error);
    connectionStatus.set("error");
  };
}

/**
 * Sends a player action to the server via WebSocket.
 * @param playerName - Name of the player taking action.
 * @param action - Action object to be sent.
 */
export function sendPlayerAction(
  playerName: string,
  action: { type: string; amount?: number }
): void {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ player_name: playerName, action }));
  } else {
    console.error("WebSocket is not open.");
  }
}
