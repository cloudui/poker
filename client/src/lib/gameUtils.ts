import type { Action } from "./types";

export function actionString(action: Action) {
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