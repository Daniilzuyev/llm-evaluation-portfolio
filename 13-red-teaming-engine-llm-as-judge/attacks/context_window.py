from core.base_attack import BaseAttack


class ContextWindow(BaseAttack):
    name = "Context Window"
    prompts: list = []

    def evaluate(self, response: str) -> bool:
        # TODO: implement disparate treatment detection
        pass