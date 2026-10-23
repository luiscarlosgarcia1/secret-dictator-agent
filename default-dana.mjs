// Default Dana is a
// deliberately predictable, non-AI protocol reference player.
function analyze(history) {
  const events = history.map((entry) => entry.event);
  const start = events.find((event) => event.type === "game-started");
  if (!start) throw new Error("missing game-started observation");

  const state = {
    seats: [...start.seats],
    you: start.you,
    knownFascists: [...start.knownFascists],
    knownDictator: start.knownDictator,
    alive: [...start.seats],
    president: start.president,
    chancellor: null,
    lastPresident: null,
    lastChancellor: null,
    investigated: new Set(),
    liberalPolicies: 0,
    fascistPolicies: 0,
    vetoRejected: false,
    presidentPolicies: [],
    chancellorPolicies: [],
  };

  for (const event of events) {
    if (event.type === "president-announced") {
      state.president = event.president;
      state.chancellor = null;
    } else if (event.type === "chancellor-nominated") {
      state.chancellor = event.chancellor;
    } else if (event.type === "government-elected") {
      state.lastPresident = event.president;
      state.lastChancellor = event.chancellor;
      state.chancellor = event.chancellor;
    } else if (event.type === "chaos-triggered") {
      state.lastPresident = null;
      state.lastChancellor = null;
    } else if (event.type === "policy-enacted") {
      if (event.policy === "liberal") state.liberalPolicies += 1;
      else state.fascistPolicies += 1;
      state.presidentPolicies = [];
      state.chancellorPolicies = [];
      state.vetoRejected = false;
    } else if (event.type === "president-cards-drawn" && event.policies) {
      state.presidentPolicies = [...event.policies];
    } else if (event.type === "chancellor-policies-received" && event.policies) {
      state.chancellorPolicies = [...event.policies];
      state.vetoRejected = false;
    } else if (event.type === "loyalty-investigated") {
      state.investigated.add(event.target);
    } else if (event.type === "player-executed") {
      state.alive = state.alive.filter((seat) => seat !== event.target);
    } else if (event.type === "veto-responded") {
      state.vetoRejected = !event.accepted;
      if (event.accepted) {
        state.presidentPolicies = [];
        state.chancellorPolicies = [];
      }
    }
  }
  return state;
}

function clockwiseChoice(state, legal) {
  const start = state.seats.indexOf(state.you.seat);
  for (let offset = 1; offset <= state.seats.length; offset += 1) {
    const candidate = state.seats[(start + offset) % state.seats.length];
    if (legal.includes(candidate)) return candidate;
  }
  throw new Error("no legal player target");
}

function legalTargets(state, kind) {
  if (kind === "nominate-chancellor") {
    return state.alive.filter((seat) =>
      seat !== state.president &&
      seat !== state.lastChancellor &&
      (state.alive.length <= 5 || seat !== state.lastPresident)
    );
  }
  return state.alive.filter((seat) =>
    seat !== state.president &&
    (kind !== "investigate-player" || !state.investigated.has(seat))
  );
}

function fallbackDecision(state, decision) {
  if (decision.kind === "nominate-chancellor") {
    return {
      type: "chancellor-nominated",
      target: clockwiseChoice(state, legalTargets(state, decision.kind)),
    };
  }
  if (decision.kind === "vote") return { type: "vote-cast", vote: "yes" };
  if (decision.kind === "president-discard") {
    // Discard Fascist first so the two-card hand contains as many Liberals as possible.
    const policy = state.presidentPolicies.includes("fascist")
      ? "fascist"
      : "liberal";
    return { type: "president-discarded", policy };
  }
  if (decision.kind === "chancellor-legislate") {
    if (state.chancellorPolicies.includes("liberal")) {
      return { type: "policy-enacted", policy: "liberal" };
    }
    if (state.fascistPolicies >= 5 && !state.vetoRejected) {
      return { type: "veto-requested" };
    }
    return { type: "policy-enacted", policy: "fascist" };
  }
  if (decision.kind === "president-veto-response") {
    return { type: "veto-responded", accepted: true };
  }
  if (decision.kind === "investigate-player") {
    return {
      type: "loyalty-investigated",
      target: clockwiseChoice(state, legalTargets(state, decision.kind)),
    };
  }
  if (decision.kind === "special-election") {
    return {
      type: "special-election-called",
      target: clockwiseChoice(state, legalTargets(state, decision.kind)),
    };
  }
  if (decision.kind === "execute-player") {
    return {
      type: "player-executed",
      target: clockwiseChoice(state, legalTargets(state, decision.kind)),
    };
  }
  if (decision.kind === "discuss") {
    return { type: "discussion-contributed" };
  }
  throw new Error("unexpected decision kind: " + decision.kind);
}

function decide(history, decision) {
  return fallbackDecision(analyze(history), decision);
}

async function handleRequest(request) {
  if (request.type === "init") return {};
  if (request.type !== "decision") throw new Error("unknown request type");
  return decide(request.history, request.decision);
}

async function run() {
  const { createInterface } = await import("node:readline");
  const lines = createInterface({ input: process.stdin, crlfDelay: Infinity });
  for await (const line of lines) {
    try {
      const response = await handleRequest(JSON.parse(line));
      process.stdout.write(JSON.stringify(response) + "\n");
    } catch (error) {
      console.error(error);
      process.exitCode = 1;
      lines.close();
      return;
    }
  }
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

export { decide };
