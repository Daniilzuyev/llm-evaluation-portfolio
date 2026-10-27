import json
from app.bot import chat
from eval.scorers import score

ATTACKS_PATH = "data/attacks.json"

def load_attacks():
    with open(ATTACKS_PATH, encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    attacks = load_attacks()
    for attack in attacks:
        reply, stop_reason = chat([], attack["prompt"])
        leaked = score(attack["risk"], reply, stop_reason)
        print(attack["id"], attack["risk"], leaked)
        if leaked:
            print(" ", reply)