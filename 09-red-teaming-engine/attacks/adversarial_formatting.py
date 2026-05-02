from core.base_attack import BaseAttack


class AdversarialFormating(BaseAttack):
    name = "Adversarial Formating"
    prompts: list = []

    def evaluate(self, response: str) -> bool:
        # TODO: implement disparate treatment detection
        pass