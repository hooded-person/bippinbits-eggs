import csv, sys, pyfiglet
import datetime as dt

f = pyfiglet.Figlet(font="cybermedium")

c = {
    "discord": False,
    "month": False,
}
for arg in sys.argv[1:]:
    if arg == "-d" or arg == "--discord":
        c["discord"] = True
    if arg == "-m" or arg == "--month":
        c["month"] = True

lastDate = dt.date.today()


data = {
    "total": 0,
    "dpy": {},
    "year": {},
    "month": {},
}

with open("eggs.csv", newline="") as file:
    reader = csv.reader(file)
    reader.__next__()  # skip headers
    for row in reader:
        date, eggs = row
        d, m, y = date.split("/")
        day, month, year = int(d), int(m), int(y)
        eggs = int(eggs)

        data["total"] = data.get("total", 0) + eggs
        data["dpy"][year] = data["dpy"].get(year, 0) + 1
        data["year"][year] = data["year"].get(year, 0) + eggs
        if not year in data["month"]:
            data["month"][year] = {}
        data["month"][year][month] = data["month"][year].get(month, 0) + eggs

        lastDate = dt.date(
            day=day,
            month=month,
            year=year,
        )


def bold(it):
    if c["discord"]:
        return "**" + str(it) + "**"
    else:
        return "\033[1m" + str(it) + "\033[0m"


def header(it):
    if c["discord"]:
        return "##" + str(it)
    else:
        return f.renderText(str(it))[0:-1]


print(header("EGGS"))
print(f"All time: {data["total"]}")
print("--------------------")
for year in data["year"]:
    eggs = data["year"][year]
    print(f"{bold(year)}: {eggs} ({data['dpy'][year]} days)")
    if c["month"]:
        for month in range(1, 13):
            if month in data["month"][year]:
                eggs = data["month"][year][month]
                monthStr = (month < 10 and " " or "") + str(month)
                print(f"   {monthStr}: {eggs}")
