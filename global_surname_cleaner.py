import csv

input_file = "global_surnames.csv"
output_file = "cleaned_global_surnames.csv"

with open(input_file, newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames

    print(f"Detected columns: {fieldnames}")
    name_col = next((col for col in fieldnames if col.lower() == "name"), None)
    if not name_col:
        raise ValueError("Couldn't find a 'name' column in the CSV.")

    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["nationality", "name"])
        writer.writeheader()

        for row in reader:
            writer.writerow({
                "nationality": row["nationality"],
                "name": row[name_col].capitalize()
            })

print(f"Cleaned global surnames written to {output_file}")
