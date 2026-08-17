import os
from anthropic import Anthropic

from attacks.privacy import Privacy
from attacks.bias_fairness import BiasFairness
from attacks.instruction_following import InstructionFollowing

from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
results = []
privacy = Privacy()
bias = BiasFairness()
instructions = InstructionFollowing()
results.extend(privacy.run(client))
results.extend(bias.run(client))
results.extend(instructions.run(client))

for result in results:
    print(result)

