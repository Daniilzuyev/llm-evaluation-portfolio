# Eval Dataset Analyzer

Утилита для анализа результатов LLM evaluation прогонов.

## Установка
```bash
pip install -r requirements.txt
```

## Использование
```python
from eval_analyzer import EvalAnalyzer

analyzer = EvalAnalyzer()
analyzer.load_data('sample_eval.csv')

# Фильтр по score
high_performers = analyzer.filter_by_score(0.8)

# Сравнение моделей
comparison = analyzer.model_comparison()
print(comparison)

# Экспорт провалов
analyzer.export_failed_tests('failed_tests.csv', threshold=0.7)
```

## Формат данных

Обязательные колонки:
- `prompt_id` — уникальный ID теста
- `model` — название модели
- `score` — оценка (0.0 - 1.0)

Опциональные:
- `latency_ms` — время ответа в миллисекундах
- `prompt_text`, `response` — текстовые данные

## Методы

- `load_data(filepath)` — загрузка CSV/JSON
- `filter_by_score(min_score)` — фильтрация по порогу
- `model_comparison()` — статистика по моделям
- `export_failed_tests(output_path, threshold)` — экспорт провалов