import csv


with open("odlr_users_csv.csv", mode='r') as csvfile:
    reader = csv.reader(csvfile, "r", delimiter=",")
    writer.writeheader(["Email"])
    line_count = 0

    for row in reader:
        if line_count == 0:
            print(f'{",".join(row)}')
            line_count += 1
        print(f'{row[0]} {row[1]} {row[2]}')
        line_count += 1
    print(f'There are {line_count} entries')
