from pathlib import Path
import pandas as pd

class EvalAnalyzer:
    def __init__(self):
        self.df = None

    def load_data(self, filepath: str):
        file_path = Path(filepath)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        if file_path.suffix == '.csv':
            self.df = pd.read_csv(file_path)
        elif file_path.suffix == '.json':
            self.df = pd.read_json(file_path)

        required = ['prompt_id', 'model', 'score']
        missing = [col for col in required if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def filter_by_score(self, min_score: float) -> pd.DataFrame:
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        mask = self.df['score'] >= min_score
        return self.df[mask]

    def model_comparison(self) -> pd.DataFrame:
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        result = self.df.groupby('model').agg(
            avg_score = ('score', 'mean'),
            min_score = ('score', 'min'),
            max_score = ('score', 'max'),
            test_count = ('score', 'count')
        ).reset_index()

        if 'latency_ms' in self.df.columns:
            latency = self.df.groupby('model')['latency_ms'].mean().reset_index()
            result = result.merge(latency, on='model')
            result.rename(columns={'latency_ms': 'avg_latency_ms'}, inplace=True)

        return result.round(2)

    def export_failed_tests(self, output_path: str, threshold: float = 0.7) -> None:
        if self.df is None:
            raise ValueError("No data loaded. Call load_data() first.")

        failed = self.df[self.df['score'] < threshold]

        output = Path(output_path)
        failed.to_csv(output, index=False)

        print(f"Exported {len(failed)} failed tests to {output_path}")


