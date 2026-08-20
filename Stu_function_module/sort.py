def sort_marks(students):

    students.sort(key=lambda x: x[2], reverse=True)

    return students