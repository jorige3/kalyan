def get_top_picks(hot_jodis, due_cycles, exhausted_jodis, num_picks=3):
    """
    Generates today's top picks based on hot, due, and exhausted jodis.

    Args:
        hot_jodis (list): List of hot Jodis.
        due_cycles (list): List of Jodis that are considered due.
        exhausted_jodis (list): List of exhausted Jodis.
        num_picks (int): The number of top picks to return.

    Returns:
        list: A list of today's top picks.
    """
    top_picks = []

    # Prioritize hot jodis that are also due
    for jodi in hot_jodis:
        if jodi in due_cycles and jodi not in exhausted_jodis:
            top_picks.append(jodi)
            if len(top_picks) >= num_picks:
                return top_picks

    # Add remaining hot jodis
    for jodi in hot_jodis:
        if jodi not in top_picks and jodi not in exhausted_jodis:
            top_picks.append(jodi)
            if len(top_picks) >= num_picks:
                return top_picks

    # Add remaining due jodis
    for jodi in due_cycles:
        if jodi not in top_picks and jodi not in exhausted_jodis:
            top_picks.append(jodi)
            if len(top_picks) >= num_picks:
                return top_picks
    
    # If still not enough picks, add from exhausted (less ideal but to fill up)
    for jodi in exhausted_jodis:
        if jodi not in top_picks:
            top_picks.append(jodi)
            if len(top_picks) >= num_picks:
                return top_picks

    return top_picks
