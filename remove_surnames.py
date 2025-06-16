import csv

input_file = "global_surnames_sorted.csv"
output_file = "global_surnames_final.csv"

with open(input_file, newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    filtered_rows = [row for row in reader if row["nationality"].strip().lower() != "english"]

fieldnames = ["nationality", "name", "ZipfPopularity"]

with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(filtered_rows)

print(f"English surnames removed. Cleaned file written to: {output_file}")
