paragraph = input("Enter a paragraph: ")

words = paragraph.split()

print("Total number of words:", len(words))
print("Number of unique words:", len(set(words)))
print("Longest word:", max(words, key=len))
print("Shortest word:", min(words, key=len))