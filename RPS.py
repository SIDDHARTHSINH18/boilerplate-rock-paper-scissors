# predicted move -> the move that beats it
BEATS = {"R": "P", "P": "S", "S": "R"}
MOVES = "RPS"

QUINCY = ["R", "R", "P", "P", "S"]

# Mirror of abbey's state (RPS_game.py:74). Its defaults are global, but it
# is only called during its own match, so we scope ours per match too.
abbey_seq = []
abbey_counts = {a + b: 0 for a in MOVES for b in MOVES}

# Per-match tally of how often each model's previous guess was right.
quincy_hits = [0] * len(QUINCY)
quincy_rounds = 0
scores = {"quincy": 0, "kris": 0, "mrugesh": 0, "abbey": 0}
last_guesses = {}


def sync_state(prev_play, my_history):
    """Mirror abbey's bookkeeping and extend the quincy phase fit."""
    global quincy_rounds, last_guesses

    if prev_play == "":
        # abbey's defaults are global, but it is only called during its own
        # match, so the plays it has observed are exactly this match's.
        abbey_seq[:] = ["R"]  # abbey substitutes "R" for the empty opener
        for key in abbey_counts:
            abbey_counts[key] = 0
        quincy_rounds = 0
        for i in range(len(quincy_hits)):
            quincy_hits[i] = 0
        for name in scores:
            scores[name] = 0
        last_guesses = {}
    else:
        abbey_seq.append(my_history[-1])
        for name in scores:
            if last_guesses.get(name) == prev_play:
                scores[name] += 1

    if len(abbey_seq) >= 2:
        abbey_counts[abbey_seq[-2] + abbey_seq[-1]] += 1

    # `prev_play in MOVES` would also accept "", since `in` on a string is
    # substring containment and "" is a substring of everything.
    if prev_play in ("R", "P", "S"):
        for phase in range(len(QUINCY)):
            if QUINCY[(phase + quincy_rounds) % len(QUINCY)] == prev_play:
                quincy_hits[phase] += 1
        quincy_rounds += 1


def guess_quincy():
    if quincy_rounds == 0:
        return "R"
    phase = max(range(len(QUINCY)), key=lambda p: quincy_hits[p])
    if quincy_hits[phase] < quincy_rounds:
        return None  # not a clean cycle, so this is not quincy
    return QUINCY[(phase + quincy_rounds) % len(QUINCY)]


def guess_kris(my_history):
    return BEATS[my_history[-1]]


def guess_mrugesh(my_history):
    recent = my_history[-10:]
    return BEATS[max(MOVES, key=recent.count)]


def guess_abbey(my_history):
    last = my_history[-1]
    counts = {last + x: abbey_counts[last + x] for x in MOVES}
    return BEATS[max(counts, key=counts.get)[-1]]


def predict(my_history):
    global last_guesses
    guesses = {
        "quincy": guess_quincy(),
        "kris": guess_kris(my_history),
        "mrugesh": guess_mrugesh(my_history),
        "abbey": guess_abbey(my_history),
    }
    viable = [name for name in guesses if guesses[name] is not None]
    best = max(viable, key=lambda name: scores[name])

    last_guesses = guesses
    return guesses[best]


def player(prev_play, opponent_history=[], my_history=[]):
    opponent_history.append(prev_play)

    # Runs before the opener branch: abbey seeds its own history with "R" on
    # this same call, so the mirror must advance even when we have no guess.
    sync_state(prev_play, my_history)

    guess = "R" if not my_history else predict(my_history)

    my_play = BEATS[guess]
    my_history.append(my_play)
    return my_play
