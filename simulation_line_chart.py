import csv
import random
import matplotlib.pyplot as plt
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

# Create weighted people based on frequencies
def make_initial_population(surnames: List[str], frequencies: List[int], pop_size: int) -> List[Tuple[str, str]]:
    weights = np.array(frequencies) / np.sum(frequencies)
    people = []
    for _ in range(pop_size):
        surname = random.choices(surnames, weights=weights)[0]
        sex = random.choice(['m', 'f'])
        people.append((surname, sex))
    return people

# Add immigrant people each generation
def inject_immigrants(immigrant_pool: Dict[str, List[Tuple[str, int]]],
                      ratios: Dict[str, float],
                      total_immigrants: int) -> List[Tuple[str, str]]:
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
            immigrants.append((surname, sex))
    return immigrants

# Reproduce next generation
def reproduce_generation(pop):
    males = [p for p in pop if p[1] == 'm']
    females = [p for p in pop if p[1] == 'f']
    random.shuffle(males)
    random.shuffle(females)
    num_pairs = min(len(males), len(females))
    new_generation = []

    for i in range(num_pairs):
        father_surname = males[i][0]
        child1_sex = random.choice(['m', 'f'])
        new_generation.append((father_surname, child1_sex))
        if random.random() < 0.44:
            child2_sex = random.choice(['m', 'f'])
            new_generation.append((father_surname, child2_sex))

    return new_generation

# Track surname counts
def write_surname_counts(population, generation_number, output_dir="surname_snapshots"):
    os.makedirs(output_dir, exist_ok=True)
    counts = Counter([p[0] for p in population])
    filename = os.path.join(output_dir, f"generation_{generation_number:02d}.csv")
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Surname", "Count"])
        for surname, count in sorted(counts.items(), key=lambda x: -x[1]):
            writer.writerow([surname, count])

# Main simulation
def run_simulation(native_file: str,
                   immigrant_file: str,
                   generations=50,
                   initial_pop_size=10000,
                   immigration_size=2000,
                   immigration_ratios=None):
    if immigration_ratios is None:
        immigration_ratios = {}

    surnames, frequencies = load_native_surnames(native_file)
    immigrant_pool = load_immigrant_surnames(immigrant_file)
    pop = make_initial_population(surnames, frequencies, initial_pop_size)
    unique_counts = []
    total_pop_counts = []

    plt.ion()
    fig, ax = plt.subplots()

    for gen in range(generations):
        immigration_fraction = 0.395
        current_population = len(pop)
        immigration_size = int(current_population * immigration_fraction)

        immigrants = inject_immigrants(immigrant_pool, immigration_ratios, immigration_size)
        pop += immigrants

        total_population = len(pop)
        unique_surnames = len(set(p[0] for p in pop))
        total_pop_counts.append(total_population)
        unique_counts.append(unique_surnames)

        print(f"Generation {gen}: {total_population} people, {unique_surnames} unique surnames")

        write_surname_counts(pop, gen)

        ax.clear()
        ax.set_title("Unique Surnames and Population Over Generations")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Count (same scale)")

        ax.plot(unique_counts, label="Unique Surnames", color='blue', marker='o')
        ax.plot(total_pop_counts, label="Total Population", color='red', marker='s')
        ax.legend()

        plt.pause(0.1)

        pop = reproduce_generation(pop)

    plt.ioff()
    plt.show()

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
        immigration_size=5000,
        immigration_ratios=immigration_ratios
    )
