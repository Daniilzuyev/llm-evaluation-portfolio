from ragas.llms import llm_factory
from ragas.embeddings import OpenAIEmbeddings
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

anthropic_client = AsyncAnthropic()
openai_client = AsyncOpenAI()

judge_llm = llm_factory(
    model="claude-sonnet-4-6",
    provider="anthropic",
    client=anthropic_client,
)
judge_llm.model_args.pop("temperature", None)
judge_llm.model_args.pop("top_p", None)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    client=openai_client
)