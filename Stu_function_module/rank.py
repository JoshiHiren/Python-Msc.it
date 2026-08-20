def rank_marks(students):

    rank = 1

    for student in students:
        student.append(rank)
        rank += 1

    return students