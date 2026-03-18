from eval_visualizer import EvalVisualizer
import pandas as pd
import numpy as np

if __name__ == "__main__":
    viz = EvalVisualizer()

    # Example 1: Prompt versions
    versions_df = pd.DataFrame({
        'version': ['v1', 'v2', 'v3', 'v4'],
        'accuracy': [0.85, 0.91, 0.88, 0.93]
    })
    viz.plot_prompt_versions(versions_df, 'prompt_versions.png')

    # Example 2: Cost vs quality
    models_df = pd.DataFrame({
        'model': ['gpt-4', 'claude-3', 'llama-3', 'gpt-3.5'],
        'cost_per_1k': [0.03, 0.015, 0.001, 0.002],
        'accuracy': [0.95, 0.92, 0.85, 0.88]
    })
    viz.plot_cost_vs_quality(models_df, 'cost_vs_quality.png')

    # Example 3: Latency boxplot
    latencies = {
        'gpt-4': [1.2, 1.5, 1.3, 1.8, 1.4, 1.6],
        'claude': [0.8, 0.7, 0.9, 0.85, 0.75, 1.1],
        'llama': [0.5, 0.6, 0.55, 0.7, 0.52, 0.8]
    }
    viz.plot_latency_boxplot(latencies, 'latency_boxplot.png')

    # Example 4: Error heatmap
    error_matrix = np.array([
        [0.05, 0.08, 0.03],
        [0.12, 0.10, 0.15],
        [0.03, 0.05, 0.04]
    ])
    categories = ['Math', 'Code', 'Summarization']
    metrics = ['Accuracy', 'Relevance', 'Coherence']
    viz.plot_error_heatmap(error_matrix, categories, 'error_heatmap.png', metrics)

    print("✅ All visualizations saved to visualizations/")