import csv
import random
from collections import Counter
import numpy as np
import os
from typing import List, Tuple, Dict

# Load base surnames (e.g., English)
def load_native_surnames(file_path: str) -> Tuple[List[str], List[int]]:
    surnames, frequencies = [], []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            surname = row['Name'].strip()
            freq = int(row['Frequency'])
            if freq > 0:
                surnames.append(surname)
                frequencies.append(freq)
    return surnames, frequencies

# Load global surnames (immigrant pool)
def load_immigrant_surnames(file_path: str) -> Dict[str, List[Tuple[str, int]]]:
    immigrants = {}
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            nationality = row['nationality'].strip()
            name = row['name'].strip()
            freq = int(row['ZipfPopularity'])
            immigrants.setdefault(nationality, []).append((name, freq))
    return immigrants

# Create initial population with native surnames
def make_initial_population(surnames: List[str], frequencies: List[int], pop_size: int) -> List[Tuple[str, str, str]]:
    weights = np.array(frequencies) / np.sum(frequencies)
    people = []
    for _ in range(pop_size):
        surname = random.choices(surnames, weights=weights)[0]
        sex = random.choice(['m', 'f'])
        people.append((surname, sex, "English"))
    return people

# Add immigrant people each generation
def inject_immigrants(immigrant_pool: Dict[str, List[Tuple[str, int]]],
                      ratios: Dict[str, float],
                      total_immigrants: int) -> List[Tuple[str, str, str]]:
    immigrants = []
    for nationality, proportion in ratios.items():
        num_people = int(total_immigrants * proportion)
        if nationality not in immigrant_pool:
            continue
        names, weights = zip(*immigrant_pool[nationality])
        norm_weights = np.array(weights) / sum(weights)
        for _ in range(num_people):
            surname = random.choices(names, weights=norm_weights)[0]
            sex = random.choice(['m', 'f'])
            immigrants.append((surname, sex, nationality))
    return immigrants

# Reproduce next generation (patrilineal surname inheritance)
def reproduce_generation(pop: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
    males = [p for p in pop if p[1] == 'm']
    females = [p for p in pop if p[1] == 'f']
    random.shuffle(males)
    random.shuffle(females)
    num_pairs = min(len(males), len(females))
    new_generation = []

    for i in range(num_pairs):
        father_surname = males[i][0]
        father_nationality = males[i][2]
        child1_sex = random.choice(['m', 'f'])
        new_generation.append((father_surname, child1_sex, father_nationality))
        if random.random() < 0.44:
            child2_sex = random.choice(['m', 'f'])
            new_generation.append((father_surname, child2_sex, father_nationality))

    return new_generation

# Write CSV file for D3 bubble visualisation
def write_surname_counts(population: List[Tuple[str, str, str]], generation_number: int, output_dir="surname-visualisations/generations"):
    os.makedirs(output_dir, exist_ok=True)
    surname_nationality_map = {}

    for surname, _, nationality in population:
        if surname not in surname_nationality_map:
            surname_nationality_map[surname] = nationality

    counts = Counter([p[0] for p in population])
    filename = os.path.join(output_dir, f"generation_{generation_number:02d}.csv")

    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Surname", "Count", "Nationality"])
        for surname, count in sorted(counts.items(), key=lambda x: -x[1]):
            nationality = surname_nationality_map.get(surname, "Unknown")
            writer.writerow([surname, count, nationality])

# Main simulation runner
def run_simulation(native_file: str,
                   immigrant_file: str,
                   generations=50,
                   initial_pop_size=10000,
                   immigration_fraction=0.395,
                   immigration_ratios=None):
    if immigration_ratios is None:
        immigration_ratios = {}

    surnames, frequencies = load_native_surnames(native_file)
    immigrant_pool = load_immigrant_surnames(immigrant_file)
    pop = make_initial_population(surnames, frequencies, initial_pop_size)

    for gen in range(generations):
        immigration_size = int(len(pop) * immigration_fraction)
        immigrants = inject_immigrants(immigrant_pool, immigration_ratios, immigration_size)
        pop += immigrants

        surname_counts = Counter([p[0] for p in pop])
        print(f"Generation {gen}: {len(pop)} people, {len(surname_counts)} unique surnames")

        write_surname_counts(pop, gen)
        pop = reproduce_generation(pop)

# Run simulation with inputs
if __name__ == "__main__":
    immigration_ratios = {
        "Indian": 0.4,
        "Russian": 0.3,
        "Polish": 0.2,
        "Arabic": 0.1,
    }

    run_simulation(
        native_file="surnames_sorted.csv",
        immigrant_file="global_surnames_final.csv",
        generations=50,
        initial_pop_size=10000,
        immigration_fraction=0.4,
        immigration_ratios=immigration_ratios
    )
