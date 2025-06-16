import csv
import numpy as np

input_file = "enriched_surnames.csv"
output_file = "global_surnames_frequencies.csv"

with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = list(csv.DictReader(csvfile))
    if len(reader) != 12366:
        raise ValueError(f"Expected 12366 surnames, found {len(reader)}")

zipf_popularity = np.random.zipf(a=1.5, size=len(reader))

for i, row in enumerate(reader):
    row["ZipfPopularity"] = str(zipf_popularity[i])

fieldnames = list(reader[0].keys())

with open(output_file, mode='w', newline='', encoding='utf-8') as outcsv:
    writer = csv.DictWriter(outcsv, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(reader)

print(f"Updated CSV with Zipf popularity written to {output_file}")
