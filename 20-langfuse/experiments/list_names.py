from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
load_dotenv()

from langfuse import get_client

langfuse = get_client()
response = langfuse.api.experiments.list(
    from_start_time=datetime.now(timezone.utc) - timedelta(days=7),
    limit=20,
)
print("found:", len(response.data))
for experiment in response.data:
    print(repr(experiment.name), experiment.item_count)