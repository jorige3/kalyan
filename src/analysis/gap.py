def last_seen_gap(df, column):
    """
    Returns how many days since each digit last appeared.
    If digit never appeared, gap = length of df.
    """
    gaps = {}

    total_len = len(df)

    for digit in range(10):
        positions = df.index[df[column] == digit].tolist()

        if positions:
            gaps[digit] = total_len - 1 - positions[-1]
        else:
            gaps[digit] = total_len  # <-- FIX HERE

    return gaps
