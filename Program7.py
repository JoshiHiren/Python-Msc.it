
from datetime import datetime


class Course:
    def __init__(self, course_code, day, start_time, end_time):
        self.course_code = course_code
        self.day = day.capitalize()
        self.start_time = start_time
        self.end_time = end_time

        # Validate time format
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")

        if start >= end:
            raise ValueError("End time must be after start time.")

    def __str__(self):
        return (f"{self.course_code} | {self.day} | "
                f"{self.start_time} - {self.end_time}")


class Student:
    def __init__(self, student_id, student_name):
        self.student_id = student_id
        self.student_name = student_name
        self.registered_courses = []

    def add_course(self, course):
        self.registered_courses.append(course)

    def detect_conflicts(self):
        conflicts = []
        courses = self.registered_courses

        for i in range(len(courses)):
            for j in range(i + 1, len(courses)):
                c1 = courses[i]
                c2 = courses[j]

                if c1.day == c2.day:
                    # Courses overlap if each starts before the other ends
                    if (c1.start_time < c2.end_time and
                            c2.start_time < c1.end_time):
                        conflicts.append((c1, c2))

        return conflicts

    def display_timetable(self):
        print("\nTimetable for", self.student_name)
        print("-" * 50)

        for course in sorted(
                self.registered_courses,
                key=lambda c: (c.day, c.start_time)):
            print(course)

    def __str__(self):
        return (f"Student ID: {self.student_id}\n"
                f"Student Name: {self.student_name}\n"
                f"Total Registered Courses: "
                f"{len(self.registered_courses)}")


def get_course_time(prompt):
    while True:
        try:
            time_value = input(prompt).strip()
            datetime.strptime(time_value, "%H:%M")
            return time_value
        except ValueError:
            print("Invalid time! Enter time in HH:MM format (24-hour).")


def main():
    students = []

    try:
        n = int(input("Enter number of students: "))

        if n <= 0:
            raise ValueError("Number of students must be positive.")

        for i in range(n):
            print(f"\nEnter details for Student {i + 1}")

            student_id = input("Student ID: ").strip()
            student_name = input("Student Name: ").strip()

            if not student_id or not student_name:
                raise ValueError("Student ID and name cannot be empty.")

            student = Student(student_id, student_name)

            number_of_courses = int(
                input("Enter number of registered courses: ")
            )

            if number_of_courses < 0:
                raise ValueError("Course count cannot be negative.")

            for j in range(number_of_courses):
                print(f"\nCourse {j + 1}")

                course_code = input("Course Code: ").strip()
                day = input(
                    "Day (Monday to Sunday): "
                ).strip().capitalize()

                valid_days = [
                    "Monday", "Tuesday", "Wednesday", "Thursday",
                    "Friday", "Saturday", "Sunday"
                ]

                if day not in valid_days:
                    raise ValueError("Invalid day of the week.")

                start_time = get_course_time("Start Time (HH:MM): ")
                end_time = get_course_time("End Time (HH:MM): ")

                course = Course(
                    course_code, day, start_time, end_time
                )
                student.add_course(course)

            students.append(student)

        # Display student details and detect conflicts
        print("\n========== REGISTRATION REPORT ==========")

        for student in students:
            print("\n" + str(student))

            conflicts = student.detect_conflicts()

            if conflicts:
                print("\nTimetable Conflicts Found:")

                for c1, c2 in conflicts:
                    print(f"Conflict: {c1.course_code} "
                          f"({c1.day}, {c1.start_time}-{c1.end_time}) "
                          f"overlaps with {c2.course_code} "
                          f"({c2.day}, {c2.start_time}-{c2.end_time})")
            else:
                print("\nNo timetable conflicts found.")
                student.display_timetable()

            print("-" * 50)

    except ValueError as error:
        print("Input Error:", error)

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")


if __name__ == "__main__":
    main()
