import csv
import random
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
import numpy as np
import os
from typing import List, Tuple, Dict

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

def load_immigrant_surnames(file_path: str) -> Tuple[Dict[str, List[Tuple[str, int]]], Dict[str, str]]:
    immigrants = defaultdict(list)
    surname_to_nationality = {}
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            nationality = row['nationality'].strip()
            name = row['name'].strip()
            freq = int(row['ZipfPopularity'])
            immigrants[nationality].append((name, freq))
            surname_to_nationality[name] = nationality
    return immigrants, surname_to_nationality

def make_initial_population(surnames: List[str], frequencies: List[int], pop_size: int) -> List[Tuple[str, str, str]]:
    weights = np.array(frequencies) / np.sum(frequencies)
    return [(random.choices(surnames, weights=weights)[0], random.choice(['m', 'f']), 'English') for _ in range(pop_size)]

def inject_immigrants(immigrant_pool: Dict[str, List[Tuple[str, int]]],
                      ratios: Dict[str, float],
                      total_immigrants: int) -> Tuple[List[Tuple[str, str, str]], Counter]:
    immigrants = []
    surname_counter = Counter()
    for nationality, proportion in ratios.items():
        if nationality not in immigrant_pool:
            continue
        names, weights = zip(*immigrant_pool[nationality])
        norm_weights = np.array(weights) / sum(weights)
        num_people = int(total_immigrants * proportion)
        for _ in range(num_people):
            surname = random.choices(names, weights=norm_weights)[0]
            sex = random.choice(['m', 'f'])
            immigrants.append((surname, sex, nationality))
            surname_counter[surname] += 1
    return immigrants, surname_counter

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

def write_surname_counts(population: List[Tuple[str, str, str]],
                         generation_number: int,
                         output_dir="surname-visualisations/generations"):
    os.makedirs(output_dir, exist_ok=True)
    surname_counts = Counter()
    surname_nationality = {}

    for surname, _, nationality in population:
        surname_counts[surname] += 1
        surname_nationality[surname] = nationality

    filename = os.path.join(output_dir, f"generation_{generation_number:02d}.csv")
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Surname", "Count", "Nationality"])
        for surname, count in sorted(surname_counts.items(), key=lambda x: -x[1]):
            nationality = surname_nationality.get(surname, "Unknown")
            writer.writerow([surname, count, nationality])

def write_generation_log(generation_number: int,
                         total_population: int,
                         unique_surnames: int,
                         cumulative_unique_surnames: int,
                         surname_counts: Counter,
                         output_dir="logs"):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"generation_{generation_number:02d}.csv")
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Generation", generation_number])
        writer.writerow(["Total Population", total_population])
        writer.writerow(["Unique Surnames", unique_surnames])
        writer.writerow(["Cumulative Unique Surnames", cumulative_unique_surnames])
        writer.writerow([])
        writer.writerow(["New Immigrant Surnames", "Count"])
        for surname, count in surname_counts.most_common():
            writer.writerow([surname, count])

def run_simulation(native_file: str,
                   immigrant_file: str,
                   generations=50,
                   initial_pop_size=10000,
                   immigration_fraction=0.395,
                   immigration_ratios=None):
    if immigration_ratios is None:
        immigration_ratios = {}

    surnames, frequencies = load_native_surnames(native_file)
    immigrant_pool, surname_to_nationality = load_immigrant_surnames(immigrant_file)
    pop = make_initial_population(surnames, frequencies, initial_pop_size)

    unique_counts = []
    total_pop_counts = []
    cumulative_surnames = set([p[0] for p in pop])

    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))

    for gen in range(generations):
        current_population = len(pop)
        immigration_size = int(current_population * immigration_fraction)

        immigrants, surname_counts = inject_immigrants(immigrant_pool, immigration_ratios, immigration_size)
        pop += immigrants

        for person in immigrants:
            cumulative_surnames.add(person[0])
        for person in pop:
            cumulative_surnames.add(person[0])

        total_population = len(pop)
        unique_surnames = len(set(p[0] for p in pop))
        cumulative_unique_surnames = len(cumulative_surnames)
        total_pop_counts.append(total_population)
        unique_counts.append(unique_surnames)

        write_generation_log(gen, total_population, unique_surnames, cumulative_unique_surnames, surname_counts)
        write_surname_counts(pop, gen)

        ax.clear()
        ax.set_title("Unique Surnames and Population Over Generations")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Count")
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
        immigration_fraction=0.395,
        immigration_ratios=immigration_ratios
    )
