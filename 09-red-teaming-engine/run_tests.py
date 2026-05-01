import os
from anthropic import Anthropic

from attacks.jailbreak import Jailbreak
from attacks.robustness import Robustness
from attacks.hallucination import Hallucination
from attacks.toxicity import Toxicity
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
# jailbreak = Jailbreak()
# robustness = Robustness()
hallucination = Hallucination()
toxicity = Toxicity()
# results = jailbreak.run(client)
# results = robustness.run(client)
# results = hallucination.run(client)
results = toxicity.run(client)

for result in results:
    print(result)

