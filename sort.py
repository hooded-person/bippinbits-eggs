import csv
from datetime import datetime
from pathlib import Path

input_path = Path(__file__).with_name("eggs.csv")

with input_path.open("r", newline="", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)


def parse_date(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%d/%m/%Y")


rows.sort(key=lambda row: parse_date(row["Date (dd/mm/yyyy)"]))

with input_path.open("w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Sorted {len(rows)} rows in {input_path}")
