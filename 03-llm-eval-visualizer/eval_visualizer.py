import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

class EvalVisualizer:
    def __init__(self, output_dir: str = 'visualizations'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def plot_prompt_versions(self, versions_df, output_file):
        plt.figure(figsize=[10, 5])
        plt.bar(versions_df['version'], versions_df['accuracy'], width=0.5, color='b')
        plt.axhline(y=0.9, color='r', linestyle='--')
        plt.xlabel('Prompt Version')
        plt.ylabel('Accuracy')
        plt.title('Prompt Version Comparison')
        plt.tight_layout()
        plt.savefig(self.output_dir / output_file)
        plt.close()

    def plot_cost_vs_quality(self, models_df, output_file):
        plt.figure(figsize=[10, 5])
        plt.scatter(models_df['cost_per_1k'], models_df['accuracy'], s=100)
        for i, row in models_df.iterrows():
            plt.text(row['cost_per_1k'], row['accuracy'], row['model'])
        plt.xlabel('Cost per 1K tokens ($)')
        plt.ylabel('Accuracy')
        plt.title('Cost vs Quality Trade-off')
        plt.grid(True, alpha=0.3)
        plt.savefig(self.output_dir / output_file)
        plt.close()

    def plot_latency_boxplot(self, latencies_by_model, output_file):
        plt.figure(figsize=[10, 5])
        data = list(latencies_by_model.values())
        labels = list(latencies_by_model.keys())
        plt.xlabel('Model')
        plt.ylabel('Latency (seconds)')
        plt.title('Latency Distribution by Model')
        plt.boxplot(data, labels=labels)
        plt.savefig(self.output_dir / output_file)
        plt.close()

    def plot_error_heatmap(self, error_matrix, categories, output_file, metrics):
        plt.figure(figsize=[10, 5])
        plt.imshow(error_matrix, cmap='Reds')
        plt.colorbar(label='Error Rate')
        plt.xticks(range(len(metrics)), metrics)
        plt.yticks(range(len(categories)), categories)
        plt.title('Error Rates by Category and Metric')
        plt.tight_layout()
        plt.savefig(self.output_dir / output_file)
        plt.close()


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
    import numpy as np

    error_matrix = np.array([
        [0.05, 0.08, 0.03],
        [0.12, 0.10, 0.15],
        [0.03, 0.05, 0.04]
    ])
    categories = ['Math', 'Code', 'Summarization']
    metrics = ['Accuracy', 'Relevance', 'Coherence']
    viz.plot_error_heatmap(error_matrix, categories, 'error_heatmap.png', metrics)

    print("✅ All visualizations saved to visualizations/")