import { fetchClient } from './fetchClient';

export async function startGame() {
  return fetchClient('start_game/');
}


