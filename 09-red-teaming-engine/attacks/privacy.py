from core.base_attack import BaseAttack


class Privacy(BaseAttack):
    name = "Privacy"
    prompts: list = []

    def evaluate(self, response: str) -> bool:
        # TODO: implement disparate treatment detection
        pass