def page_rank(links, num_iterations=20, initial_pr=1.0):
    rank = {}
    for (from_id, to_id) in links:
        if from_id not in rank:
            rank[from_id] = 0.0

    for (from_id, to_id) in links:
        if to_id in rank:
            rank[to_id] += 1.0
    return rank
