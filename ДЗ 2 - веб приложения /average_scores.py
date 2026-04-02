def compute_average_scores(scores):
    return tuple(sum(student)/len(student) for student in zip(*scores))
