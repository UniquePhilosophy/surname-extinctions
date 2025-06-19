import csv
from collections import defaultdict

def scale_frequencies_by_ratio(input_file: str, output_file: str, target_ratio: int = 775):
    surname_data = defaultdict(list)

    with open(input_file, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            nationality = row['nationality']
            name = row['name']
            freq = int(row['ZipfPopularity'])
            surname_data[nationality].append((name, freq))

    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['nationality', 'name', 'ZipfPopularity']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for nationality, surnames in surname_data.items():
            freqs = [f for _, f in surnames]
            min_f, max_f = min(freqs), max(freqs)

            if min_f == max_f:
                for name, _ in surnames:
                    writer.writerow({'nationality': nationality, 'name': name, 'ZipfPopularity': 1})
                continue

            for name, freq in surnames:
                scaled = 1 + ((freq - min_f) * (target_ratio - 1)) / (max_f - min_f)
                writer.writerow({'nationality': nationality, 'name': name, 'ZipfPopularity': int(round(scaled))})

if __name__ == "__main__":
    scale_frequencies_by_ratio(
        input_file='global_surnames_bad_weightings.csv',
        output_file='global_surnames_final.csv',
        target_ratio=775
    )
