n = tuple(input())

for i in range(len(n) - 1):
    if n[i] == n[i + 1]:
        if i == 0 or n[i] != n[i - 1]:
            print(n[i])
