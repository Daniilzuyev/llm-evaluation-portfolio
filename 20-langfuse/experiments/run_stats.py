import statistics
import sys
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
load_dotenv()

from langfuse import get_client

LOOKBACK = timedelta(days=7)


def run_stats(experiment_name: str) -> dict:
    langfuse = get_client()
    since = datetime.now(timezone.utc) - LOOKBACK

    response = langfuse.api.experiments.list_items(
        from_start_time=since,
        experiment_name=experiment_name,
        limit=100,
    )

    latencies = []
    total_cost = 0.0
    input_tokens = 0
    output_tokens = 0

    for item in response.data:
        observations = langfuse.api.observations.get_many(
            trace_id=item.trace_id,
            fields="core,basic,usage,metrics",
            from_start_time=since,
            limit=100,
        ).data

        for obs in observations:
            if obs.is_root_observation and obs.latency is not None:
                latencies.append(obs.latency)
            if obs.type == "GENERATION":
                total_cost += obs.total_cost or 0.0
                usage = obs.usage_details or {}
                input_tokens += usage.get("input", 0)
                output_tokens += usage.get("output", 0)

    return {
        "run": experiment_name,
        "items": len(response.data),
        "p50_latency_s": round(statistics.median(latencies), 3) if latencies else None,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(total_cost, 6),
    }


if __name__ == "__main__":
    for name in sys.argv[1:]:
        print(run_stats(name))