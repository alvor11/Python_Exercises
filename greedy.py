def main():
    while True:    
        try:
            money = float(input(" hai! How much change is owed? "))
            if money > 0:
                break
        except ValueError:
            print("Введите число > 0")
    count = 0
    coins = [25, 10, 5, 1]
    for item in coins:
        count += money // item
        money = money % item
    print(count)
        
if __name__ == "__main__":
    main()
