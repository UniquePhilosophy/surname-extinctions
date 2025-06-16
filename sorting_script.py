import csv

input_file = "global_surnames_frequencies.csv"
output_file = "global_surnames_sorted.csv"

with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = list(csv.DictReader(csvfile))

sorted_rows = sorted(reader, key=lambda row: int(row['ZipfPopularity']), reverse=True)

fieldnames = sorted_rows[0].keys()
with open(output_file, mode='w', newline='', encoding='utf-8') as outcsv:
    writer = csv.DictWriter(outcsv, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(sorted_rows)

print(f"Sorted CSV written to: {output_file}")
