from core.base_attack import BaseAttack


class BiasFairness(BaseAttack):
    name = "Bias & Fairness"
    prompts: list = []

    def evaluate(self, response: str) -> bool:
        # TODO: implement disparate treatment detection
        pass