def get_student_data():

    n = int(input("Enter number of students: "))

    students = []

    for i in range(n):

        roll = input("Enter Roll No: ")
        name = input("Enter Name: ")

        marks = []

        for j in range(5):
            mark = int(input("Enter marks: "))
            marks.append(mark)

        total = sum(marks)
        percentage = total / 5

        if percentage >= 90:
            grade = "A+"
        elif percentage >= 80:
            grade = "A"
        elif percentage >= 70:
            grade = "B"
        elif percentage >= 60:
            grade = "C"
        elif percentage >= 50:
            grade = "D"
        else:
            grade = "F"

        students.append([roll, name, total, percentage, grade])

    return students