import datetime as dt

lastDate = dt.date.today()

with open("eggs.csv", "a", newline="") as file:
    while True:
        date = lastDate.strftime("%d/%m/%Y")
        eggs = input(date + ", ")
        if eggs:
            print(date + ", " + eggs, file=file, flush=True)
        lastDate = lastDate - dt.timedelta(days=1)
