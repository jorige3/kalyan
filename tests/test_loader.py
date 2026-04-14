from src.data.loader import DataLoader


def test_data_loader_basic(tmp_path):
    # Create a dummy CSV
    d = tmp_path / "data"
    d.mkdir()
    csv = d / "kalyan.csv"
    csv.write_text(
        "date,open_panel,jodi,close_panel,sangam\n2023-01-01,123,45,678,123-678\n2023-01-02,234,xx,789,234-789"
    )

    loader = DataLoader(str(csv))
    df = loader.load_data()

    assert len(df) == 1
    assert df.iloc[0]["jodi"] == "45"
    assert df.iloc[0]["open_digit"] == 4
    assert df.iloc[0]["close_digit"] == 5


def test_data_loader_numeric_filter(tmp_path):
    csv = tmp_path / "kalyan_filter.csv"
    csv.write_text(
        "date,open_panel,jodi,close_panel,sangam\n2023-01-01,123,45,678,123-678\n2023-01-02,234,9*,789,234-789"
    )

    loader = DataLoader(str(csv))
    df = loader.load_data()

    assert len(df) == 1
    assert "9*" not in df["jodi"].values
