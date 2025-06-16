import csv

global_file = "cleaned_global_surnames.csv"
indian_file = "indian_surnames.csv"
output_file = "enriched_surnames.csv"

with open(global_file, newline='', encoding='utf-8') as infile:
    global_surnames = list(csv.DictReader(infile))

with open(indian_file, newline='', encoding='utf-8') as indian_csv:
    reader = csv.DictReader(indian_csv)
    indian_surnames = [{"nationality": "Indian", "name": row["Name"].capitalize()} for row in reader]

combined = global_surnames + indian_surnames

with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=["nationality", "name"])
    writer.writeheader()
    writer.writerows(combined)

print(f"Combined global and Indian surnames written to {output_file}")
