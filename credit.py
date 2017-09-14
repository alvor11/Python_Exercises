def main():
    while True:    
        try:
            number = input("Введите номер карты: ")
            if int(number) > 999999999999:
                break
        except ValueError:
            print("Введите правильный номер карты")
    sum = credit(number)
    if int(number) < 4000000000000 or int(number) >= 5600000000000000 or sum % 10 != 0:
        print("INVALID")
    if (int(number) >= 4000000000000 and int(number) < 5000000000000) or (int(number) >= 4000000000000000 and int(number) < 5000000000000000):
        print("VISA")
    elif int(number) >= 5100000000000000 and int(number) < 5600000000000000:
        print("MASTERCARD")
    elif (int(number) >= 340000000000000 and int(number) < 350000000000000) or (int(number) >= 370000000000000 and int(number) < 380000000000000):
        print("AMEX")
    else:
        print("INVALID")
def credit (num):
    count = 0
    sum1 = 0
    sum2 = 0
    tmp = 0
    for letter in num:
        if count % 2 != 0:
            sum1 += int(num[count])
        else:
            tmp = int(num[count]) * 2
            if tmp // 10 == 0:
                sum2 += tmp
            else:
                sum2 += tmp[0] + tmp[1]
    return sum1 + sum2            
            
    
    
    
if __name__ == "__main__":
    main()
