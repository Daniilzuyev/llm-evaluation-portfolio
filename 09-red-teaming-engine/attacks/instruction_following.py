from core.base_attack import BaseAttack


class InstructionFollowing(BaseAttack):
    name = "Instruction Following"
    prompts: list = []

    def evaluate(self, response: str) -> bool:
        # TODO: implement disparate treatment detection
        pass