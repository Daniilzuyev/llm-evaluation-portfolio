import json
from app.bot import chat
from eval.scorers import score

ATTACKS_PATH = "data/attacks.json"
REPEATS = 3

def load_attacks():
    with open(ATTACKS_PATH, encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    attacks = load_attacks()
    for attack in attacks:
        success = 0
        for _ in range(REPEATS):
            reply, stop_reason = chat ([], attack["prompt"])
            leaked = score(attack["risk"], reply, stop_reason)

            if leaked:
                success += 1
                print(" ", reply)

        print(attack["id"], attack["risk"], f"{success / REPEATS}")
