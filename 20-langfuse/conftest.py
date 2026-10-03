import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
os.environ["LANGFUSE_TRACING_ENABLED"] = "false"
os.environ.setdefault("ANTHROPIC_API_KEY", "12345")