password = input("Enter Password: ")

upper = False
lower = False
digit = False
special = False
repeat = False

sp = "!@#$%^&*()-_=+"

for i in range(len(password)):
    ch = password[i]

    if ch >= 'A' and ch <= 'Z':
        upper = True

    if ch >= 'a' and ch <= 'z':
        lower = True

    if ch >= '0' and ch <= '9':
        digit = True

    if ch in sp:
        special = True

    if i > 0 and password[i] == password[i-1]:
        repeat = True

print("\nResult:")

if not upper:
    print("Uppercase missing")

if not lower:
    print("Lowercase missing")

if not digit:
    print("Digit missing")

if not special:
    print("Special character missing")

if repeat:
    print("Repeated character found")

if upper and lower and digit and special and not repeat:
    print("Strong Password")
else:
    print("Weak Password")
