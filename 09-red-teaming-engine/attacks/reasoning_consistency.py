from core.base_attack import BaseAttack


class ReasoningConsistency(BaseAttack):
    name = "Reasoning Consistency"
    prompts: list = []

    def evaluate(self, response: str) -> bool:
        # TODO: implement disparate treatment detection
        pass