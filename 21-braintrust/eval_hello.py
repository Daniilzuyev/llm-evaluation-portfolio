from dotenv import load_dotenv
from braintrust import Eval
from autoevals import ExactMatch

load_dotenv()

Eval(
    "Say Hi Bot",
    data=lambda: [
        {"input": "Foo", "expected": "Hi Foo"},
        {"input": "Bar", "expected": "Hello Bar"},
    ],
    task=lambda input: "Hi " + input,
    scores=[ExactMatch],
)