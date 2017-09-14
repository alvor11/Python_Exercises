import sys


if len(sys.argv) != 2 or (sys.argv[1]).isdigit() != True:
    print("Введиде цифровой код")
    exit(1)
key = int(sys.argv[1])
if key > 0:
    while True:
        try:
            text = input("plaintext:")
        except ValueError:
            print("Введите текст")
        if text != None:
            break
print("ciphertext:", end="")
for char in text:
    if char.isalpha():
        if char.isupper():
            char = ((ord(char) - ord('A')) + key) % 26
            print(chr(char + ord('A')), end="")
        else:
            char = ((ord(char) - ord('a')) + key) % 26
            print(chr(char + ord('a')), end="")
    else:
        print(char, end="")
print()

