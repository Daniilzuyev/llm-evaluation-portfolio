from experiments.cases import make_data

def test_make_data_shape():
    rows = make_data()
    assert len(rows) == 12
    assert set(rows[0].keys()) == {"input", "expected", "metadata"}