import csv
import datetime as dt

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

c = {
    "month": False,
}

print("## EGGS")
print(f"All time: {data["total"]}")
for year in data["year"]:
    eggs = data["year"][year]
    print(f"**{year}**: {eggs} ({data['dpy'][year]} days)")
    if c["month"]:
        for month in data["month"][year]:
            eggs = data["month"][year][month]
            print(f"   {month}: {eggs}")
