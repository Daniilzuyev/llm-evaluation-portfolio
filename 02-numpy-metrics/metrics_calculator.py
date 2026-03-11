import json
from typing import List

import pandas as pd
import numpy as np
from path import Path


class MetricsCalculator:
    def __init__(self, csv_path: str):
        if not Path(csv_path).exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        self.csv_path = csv_path
        self.df = pd.read_csv(self.csv_path)
        self.scores = np.array(self.df['score'])

    def calculate_statistics(self) -> dict:
        """
        Calculate basic statistics for evaluation scores.

        Returns:
            dict: Contains mean, median, std, min, max, range, p95, pass_rate
        """
        return {
            'mean': self.scores.mean(),
            'median': np.median(self.scores),
            'std': self.scores.std(),
            'min': self.scores.min(),
            'max': self.scores.max(),
            'range': self.scores.max() - self.scores.min(),
            'p95': np.percentile(self.scores, 95),
            'pass_rate': (self.scores >= 0.7).sum() / len(self.scores)
        }
    def detect_anomalies(self, threshold: float = 2.0) -> List:
        """
            Detect anomalies using z-score analysis.

            Args:
                threshold: Z-score threshold for anomaly detection (default: 2.0)

            Returns:
                list[dict]: Anomalies with 'index', 'score', and 'z_score' fields
        """
        mean = self.scores.mean()
        std = self.scores.std()

        z_scores = (self.scores - mean) / std
        anomaly_indices = np.where(np.abs(z_scores) > threshold)[0]

        anomalies = []
        for idx in anomaly_indices:
            anomalies.append({
                'index': int(idx),
                'score': float(self.scores[idx]),
                'z_score': float(z_scores[idx])
            })
        return anomalies

    def compare_runs(self, other_csv: str) -> dict:
        other_df = pd.read_csv(other_csv)
        other_scores = np.array(other_df['score'])

        baseline_mean = self.scores.mean()
        experiment_mean = other_scores.mean()

        improvement = experiment_mean - baseline_mean
        improvement_pct = (improvement / baseline_mean) * 100

        return {
            'baseline_mean': float(baseline_mean),
            'experiment_mean': float(experiment_mean),
            'improvement': float(improvement),
            'improvement_pct': float(improvement_pct),
        }

    def save_report(self, output_path: str):
        report = {
            'file': self.csv_path,
            'total_samples': len(self.scores),
            'statistics': self.calculate_statistics(),
            'anomalies': self.detect_anomalies()
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)


if __name__ == '__main__':
    # Baseline прогон
    calc = MetricsCalculator('eval_run_baseline.csv')

    print("=== Base Statistics ===")
    stats = calc.calculate_statistics()
    for key, value in stats.items():
        print(f"{key:15} = {value:.4f}")

    print("\n=== Anomalies (z-score > 2.0) ===")
    anomalies = calc.detect_anomalies(threshold=2.0)
    print(f"Found: {len(anomalies)}")
    for a in anomalies:
        print(f"  Index {a['index']}: score={a['score']:.4f}, z-score={a['z_score']:.2f}")

    print("\n=== Compare Runs ===")
    comparison = calc.compare_runs('eval_run_experiment.csv')
    for key, value in comparison.items():
        print(f"{key:20} = {value:.4f}")

    print("\n=== Save Report ===")
    calc.save_report('metrics_report.json')
    print("✓ Report is saved in metrics_report.json")
