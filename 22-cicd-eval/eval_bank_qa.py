from braintrust import Eval
from app.pipeline import answer_pipeline
from experiments.cases import make_data
from experiments.scorers import no_phone_number, matches_expected

Eval(
    "Imagine Bank Support QA",
    experiment_name="tokenize-singular",
    data=make_data,
    task=answer_pipeline,
    scores=[no_phone_number, matches_expected]
)