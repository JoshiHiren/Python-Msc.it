
from datetime import datetime


class Course:
    def __init__(self, course_code, day, start_time, end_time):
        self.course_code = course_code
        self.day = day.capitalize()
        self.start_time = self.validate_time(start_time)
        self.end_time = self.validate_time(end_time)

        if self.start_time >= self.end_time:
            raise ValueError("End time must be later than start time.")

    @staticmethod
    def validate_time(time_string):
        try:
            return datetime.strptime(time_string, "%H:%M").time()
        except ValueError:
            raise ValueError("Invalid time. Enter time in HH:MM format.")

    def __str__(self):
        return (
            f"{self.course_code} | {self.day} | "
            f"{self.start_time.strftime('%H:%M')} - "
            f"{self.end_time.strftime('%H:%M')}"
        )


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
                course1 = courses[i]
                course2 = courses[j]

                if course1.day == course2.day:
                    # Two courses conflict if their time intervals overlap.
                    if (
                        course1.start_time < course2.end_time
                        and course2.start_time < course1.end_time
                    ):
                        conflicts.append((course1, course2))

        return conflicts

    def display_timetable(self):
        print("\nTimetable:")
        if not self.registered_courses:
            print("No courses registered.")
            return

        days = [
            "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"
        ]

        for day in days:
            day_courses = [
                course for course in self.registered_courses
                if course.day == day
            ]

            day_courses.sort(key=lambda c: c.start_time)

            for course in day_courses:
                print(course)

    def __str__(self):
        return (
            f"\nStudent ID: {self.student_id}\n"
            f"Student Name: {self.student_name}\n"
            f"Total Registered Courses: {len(self.registered_courses)}"
        )


def read_integer(prompt, minimum=0):
    while True:
        try:
            value = int(input(prompt))
            if value < minimum:
                print(f"Please enter a number greater than or equal to {minimum}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a whole number.")


def main():
    students = []

    valid_days = {
        "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday"
    }

    number_of_students = read_integer(
        "Enter the number of students: ", 1
    )

    for i in range(number_of_students):
        print(f"\n--- Student {i + 1} ---")

        student_id = input("Enter Student ID: ").strip()
        student_name = input("Enter Student Name: ").strip()

        while not student_id or not student_name:
            print("Student ID and name cannot be empty.")
            student_id = input("Enter Student ID: ").strip()
            student_name = input("Enter Student Name: ").strip()

        student = Student(student_id, student_name)

        number_of_courses = read_integer(
            "Enter the number of registered courses: ", 0
        )

        for j in range(number_of_courses):
            print(f"\nCourse {j + 1}")

            while True:
                try:
                    course_code = input("Enter Course Code: ").strip()
                    if not course_code:
                        raise ValueError("Course code cannot be empty.")

                    day = input("Enter Day of the Week: ").strip().capitalize()
                    if day.lower() not in valid_days:
                        raise ValueError(
                            "Invalid day. Enter a day from Monday to Sunday."
                        )

                    start_time = input("Enter Start Time (HH:MM): ").strip()
                    end_time = input("Enter End Time (HH:MM): ").strip()

                    course = Course(
                        course_code, day, start_time, end_time
                    )
                    student.add_course(course)
                    break

                except ValueError as error:
                    print(f"Error: {error}")
                    print("Please enter the course details again.\n")

        students.append(student)

    print("\n========== REGISTRATION REPORT ==========")

    for student in students:
        print(student)

        conflicts = student.detect_conflicts()

        if conflicts:
            print("\nTimetable Conflicts Found:")
            for course1, course2 in conflicts:
                print(f"Conflict: [{course1}] overlaps with [{course2}]")
        else:
            print("\nNo timetable conflicts found.")
            student.display_timetable()

        print("-" * 45)


if __name__ == "__main__":
    main()

