def main():
    while True:
        try:
            height = int(input("Height: "))
        except ValueError:
            print("введите число от 0 до 24")
        if height > 0 and height < 23:
            break
    i = 0
    while i < height:
        print(" " * (height - i) + "#" * (i + 1) + "  " + "#" * (i + 1))
        i = i + 1
        
if __name__ == "__main__":
    main()

