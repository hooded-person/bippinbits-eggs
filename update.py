import sys
import datetime as dt

max = -1
if sys.argv[1] == "--once":
    max = 1

lastDate = dt.date.today()

with open("eggs.csv", "a", newline="") as file:
    count = 0
    while count != max:
        date = lastDate.strftime("%d/%m/%Y")
        eggs = input(date + ", ")
        if eggs:
            print(date + ", " + eggs, file=file, flush=True)
        lastDate = lastDate - dt.timedelta(days=1)
        count += 1
