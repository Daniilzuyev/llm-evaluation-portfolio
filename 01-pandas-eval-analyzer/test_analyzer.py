from eval_analyzer import EvalAnalyzer


def main():
    analyzer = EvalAnalyzer()

    print("=== Loading data ===")
    analyzer.load_data('sample_eval.csv')
    print("✓ Data loaded successfully\n")

    print("=== High-score tests (>= 0.8) ===")
    high_score = analyzer.filter_by_score(0.8)
    print(high_score[['prompt_id', 'model', 'score']])
    print()

    print("=== Model comparison ===")
    comparison = analyzer.model_comparison()
    print(comparison)
    print()

    print("=== Exporting failed tests ===")
    analyzer.export_failed_tests('failed_tests.csv', threshold=0.7)
    print()


if __name__ == "__main__":
    main()