import { writable } from 'svelte/store';
import type { Action } from '$lib/types';


type ActionState = {
  bet: Action | null;
  raise: Action | null;
  fold: Action | null;
  check: Action | null;
  call: Action | null;
};

export const actionState = writable<ActionState>({
  bet: null,
  raise: null,
  fold: null,
  check: null,
  call: null,
});

export function parseActions(actions: Action[]) {
  let betAction = null;
  let raiseAction = null;
  let foldAction = null;
  let checkAction = null;
  let callAction = null;

  for (const action of actions) {
    switch (action.type.toLowerCase()) {
      case "bet":
        betAction = action;
        break;
      case "raise":
        raiseAction = action;
        break;
      case "fold":
        foldAction = action;
        break;
      case "check":
        checkAction = action;
        break;
      case "call":
        callAction = action;
        break;
      default:
        break;
    }
  }

  actionState.set({
    bet: betAction,
    raise: raiseAction,
    fold: foldAction,
    check: checkAction,
    call: callAction,
  })
}