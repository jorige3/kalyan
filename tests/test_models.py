import pandas as pd
import pytest

from src.models.ensemble_model import EnsembleModel
from src.models.heat_model import HeatModel
from src.models.matrix_model import MatrixModel
from src.models.momentum_model import MomentumModel


@pytest.fixture
def sample_df():
    data = {
        "date": pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"]),
        "jodi": ["11", "22", "33"],
        "open_panel": ["123", "234", "345"],
        "close_panel": ["678", "789", "890"],
        "sangam": ["123-678", "234-789", "345-890"],
        "open_digit": [1, 2, 3],
        "close_digit": [1, 2, 3],
    }
    return pd.DataFrame(data)


def test_heat_model(sample_df):
    model = HeatModel()
    preds = model.predict(sample_df)
    assert not preds.empty
    assert "jodi" in preds.columns
    assert "score" in preds.columns


def test_matrix_model(sample_df):
    model = MatrixModel()
    preds = model.predict(sample_df)
    assert not preds.empty


def test_momentum_model(sample_df):
    model = MomentumModel()
    preds = model.predict(sample_df)
    assert not preds.empty


def test_ensemble_model(sample_df):
    h = HeatModel()
    ma = MatrixModel()
    mo = MomentumModel()
    ensemble = EnsembleModel(h, ma, mo)
    preds = ensemble.predict(sample_df)
    assert not preds.empty
    assert preds.iloc[0]["rank"] == 1
