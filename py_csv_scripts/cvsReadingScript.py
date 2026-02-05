import csv


#keep the file open and place it in a variable
with open("odlr_users_csv.csv", mode='r') as test_file:
    reader = csv.reader(test_file, delimiter=',')
    line_count = 0
    for row in reader:
        if line_count == 0:
            print(f'{",".join(row)}')
            line_count += 1
        print(f'{row[0]} {row[1]} {row[2]}')
        line_count += 1
    print(f'There are {line_count} entries')
