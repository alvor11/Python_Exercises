#test
file = open("sentiments/positive-words.txt")
my_list = []
for line in file:
    if line.startswith(";", 0) or str.isspace(line):
        continue
    else:
        my_list.append(str.strip(line)) 
my_list = tuple(my_list)
print(my_list)
