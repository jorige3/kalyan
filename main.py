from src.loaders.data_loader import load_data


def main() -> None:
    df = load_data()
    print("✅ Data loaded")
    print(df.tail(5))


if __name__ == "__main__":
    main()
