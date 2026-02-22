import os

import pandas as pd
import pytest

from src.engine.kalyan_engine import KalyanEngine


# Fixture to create a dummy kalyan.csv for testing
@pytest.fixture
def dummy_kalyan_csv(tmp_path):
    csv_path = tmp_path / "kalyan.csv"
    dummy_data = {
        'date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10']),
        'open_panel': ['128', '238', '348', '458', '568', '678', '788', '898', '908', '118'],
        'jodi': ['12', '23', '34', '45', '56', '67', '78', '89', '90', '11'],
        'close_panel': ['480', '580', '680', '780', '880', '980', '080', '180', '280', '380'],
        'sangam': ['128-480', '238-580', '348-680', '458-780', '568-880', '678-980', '788-080', '898-180', '908-280', '118-380']
    }
    pd.DataFrame(dummy_data).to_csv(csv_path, index=False)
    return str(csv_path)

# Fixture to ensure no kalyan.csv exists
@pytest.fixture
def no_kalyan_csv(tmp_path):
    csv_path = tmp_path / "kalyan.csv"
    # Ensure it doesn't exist before test
    if os.path.exists(csv_path):
        os.remove(csv_path)
    return str(csv_path)

def test_kalyan_engine_loads_existing_data(dummy_kalyan_csv):
    engine = KalyanEngine(csv_path=dummy_kalyan_csv)
    assert not engine.df.empty
    assert len(engine.df) == 10
    assert all(col in engine.df.columns for col in ['date', 'open', 'jodi', 'close', 'open_sangam', 'close_sangam'])
    # check that open and close are derived correctly
    assert engine.df['open'].tolist() == [1, 2, 3, 4, 5, 6, 7, 8, 9, 1]
    assert engine.df['close'].tolist() == [2, 3, 4, 5, 6, 7, 8, 9, 0, 1]
    # check that panels were renamed
    assert engine.df['open_sangam'].tolist() == ['128', '238', '348', '458', '568', '678', '788', '898', '908', '118']
    assert engine.df['close_sangam'].tolist() == ['480', '580', '680', '780', '880', '980', '080', '180', '280', '380']

def test_kalyan_engine_generates_dummy_data_if_no_csv(no_kalyan_csv):
    engine = KalyanEngine(csv_path=no_kalyan_csv)
    assert not engine.df.empty
    assert len(engine.df) > 0  # Should generate some dummy data
    assert all(col in engine.df.columns for col in ['date', 'open', 'jodi', 'close', 'open_sangam', 'close_sangam'])

