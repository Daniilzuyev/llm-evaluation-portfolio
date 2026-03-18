# LLM Eval Visualizer

Matplotlib-based visualization toolkit for LLM evaluation metrics. Creates publication-ready charts for model comparison, cost analysis, latency distribution, and error pattern analysis.

## Use Cases

### 1. Prompt Version Comparison (`plot_prompt_versions`)
**Problem:** You've iterated through 4 prompt versions. Which one performs best?

**Solution:** Bar chart with accuracy threshold line shows v4 exceeds the 0.9 target.

**When to use:**
- A/B testing prompts
- Tracking prompt engineering improvements
- Presenting results to stakeholders

---

### 2. Cost vs Quality Trade-off (`plot_cost_vs_quality`)
**Problem:** GPT-4 is accurate but expensive. Can you find a cheaper model with acceptable quality?

**Solution:** Scatter plot reveals the "sweet spot" — Claude-3 offers 92% accuracy at half the cost.

**When to use:**
- Budget optimization
- Model selection decisions
- ROI analysis for production deployments

---

### 3. Latency Distribution (`plot_latency_boxplot`)
**Problem:** Users complain about inconsistent response times. Which model is most reliable?

**Solution:** Boxplot shows GPT-4 has high median latency (1.5s) with outliers up to 1.8s, while Claude is consistently under 1s.

**When to use:**
- SLA compliance checks
- Performance regression testing
- Identifying models with unpredictable behavior

---

### 4. Error Heatmap (`plot_error_heatmap`)
**Problem:** Your eval suite has 500 test cases across Math, Code, and Summarization categories. Where are the failures concentrated?

**Solution:** Heatmap reveals Code tasks have 12% accuracy errors and 15% coherence errors — a clear signal to improve code-related prompts.

**When to use:**
- Root cause analysis for eval failures
- Identifying weak areas in model capabilities
- Prioritizing prompt improvements

---

## Installation
```bash
pip install matplotlib pandas numpy
```

## Usage
```python
from eval_visualizer import EvalVisualizer
import pandas as pd

viz = EvalVisualizer()

# Prompt version comparison
versions_df = pd.DataFrame({
    'version': ['v1', 'v2', 'v3', 'v4'],
    'accuracy': [0.85, 0.91, 0.88, 0.93]
})
viz.plot_prompt_versions(versions_df, 'prompt_versions.png')
```

See `example_usage.py` for complete examples of all 4 methods.

## Output

All charts save to `visualizations/` directory as PNG files, ready for:
- Embedding in reports
- Sharing in Slack/email
- Including in CI/CD dashboards

## Why These Visualizations Matter in LLM Evaluation

Unlike traditional ML (where you have thousands of labeled examples), LLM evaluation often involves:
- Small datasets (50-500 examples)
- Multiple competing metrics (accuracy, cost, latency)
- Qualitative categories (Math vs Code vs Summarization)

These 4 visualizations are specifically designed for the **multi-dimensional, small-sample** nature of LLM eval work.

## Project Structure
```
03-llm-eval-visualizer/
├── eval_visualizer.py      # Main class with 4 visualization methods
├── example_usage.py        # Demo with realistic eval data
├── visualizations/         # Output directory (auto-created)
│   ├── prompt_versions.png
│   ├── cost_vs_quality.png
│   ├── latency_boxplot.png
│   └── error_heatmap.png
└── README.md
```

## Skills Demonstrated

- Matplotlib figure management (`plt.figure`, `plt.close`)
- Multiple plot types (bar, scatter, boxplot, heatmap)
- Production-ready patterns (no `plt.show()`, proper memory cleanup)
- Domain-specific visualization design for LLM evaluation