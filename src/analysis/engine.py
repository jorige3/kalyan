from .frequency import digit_frequency
from .gap import last_seen_gap
from .scoring import weighted_score


def run_analysis(df):
    result = {}

    for col in ["open", "close"]:
        freq = digit_frequency(df, col)
        gap = last_seen_gap(df, col)

        score = weighted_score(freq.to_dict(), gap)

        result[col] = {
            "frequency": freq.to_dict(),
            "gap": gap,
            "score": score.to_dict()
        }

    return result

