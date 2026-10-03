def test_imports():
    from app.retriever import retrieve
    assert callable(retrieve)