n = int(input("Enter number of students: "))

students = []

for i in range(n):
    roll = int(input("Enter Roll No: "))
    name = input("Enter Name: ")

    total = 0
    for j in range(5):
        marks = int(input("Enter Marks: "))
        total = total + marks

    percentage = total / 5

    if percentage >= 90:
        grade = "A"
    elif percentage >= 80:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    else:
        grade = "F"

    students.append([roll, name, total, percentage, grade])

students.sort(key=lambda x: x[3], reverse=True)

print("\nRoll\tName\tTotal\tPercentage\tGrade\tRank")

for i in range(n):
    rank = i + 1

    if i > 0 and students[i][3] == students[i-1][3]:
        rank = students[i-1][5]

    students[i].append(rank)

    print(students[i][0], "\t", students[i][1], "\t",
          students[i][2], "\t", students[i][3], "\t\t",
          students[i][4], "\t", students[i][5])
