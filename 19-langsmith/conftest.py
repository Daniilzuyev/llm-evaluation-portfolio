import os
import sys
from pathlib import Path

# Tests must never send traces or call live APIs.
os.environ["LANGSMITH_TRACING"] = "false"

sys.path.insert(0, str(Path(__file__).parent))