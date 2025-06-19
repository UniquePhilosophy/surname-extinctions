import csv
import random
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import os
from typing import List, Tuple

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

def make_initial_population(surnames: List[str], frequencies: List[int], pop_size: int) -> List[Tuple[str, str, str]]:
    weights = np.array(frequencies) / np.sum(frequencies)
    half = pop_size // 2
    males = [(random.choices(surnames, weights=weights)[0], 'm', 'English') for _ in range(half)]
    females = [(random.choices(surnames, weights=weights)[0], 'f', 'English') for _ in range(pop_size - half)]
    return males + females

def reproduce_generation(pop: List[Tuple[str, str, str]],
                         mean_children_per_couple: float = 2.0) -> List[Tuple[str, str, str]]:
    males = [p for p in pop if p[1] == 'm']
    females = [p for p in pop if p[1] == 'f']
    random.shuffle(males)
    random.shuffle(females)
    num_pairs = min(len(males), len(females))
    new_generation = []

    for i in range(num_pairs):
        father_surname = males[i][0]
        nationality = males[i][2]

        num_children = np.random.poisson(mean_children_per_couple)

        for _ in range(num_children):
            sex = random.choice(['m', 'f'])
            new_generation.append((father_surname, sex, nationality))

    desired_pop_size = len(pop)
    current_pop_size = len(new_generation)

    if current_pop_size == 0:
        return []

    if current_pop_size != desired_pop_size:
        new_generation = random.choices(new_generation, k=desired_pop_size)

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
                         output_dir="logs"):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"generation_{generation_number:02d}.csv")
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Generation", generation_number])
        writer.writerow(["Total Population", total_population])
        writer.writerow(["Unique Surnames", unique_surnames])
        writer.writerow(["Cumulative Unique Surnames", cumulative_unique_surnames])

def run_simulation(native_file: str,
                   generations=50,
                   initial_pop_size=10000,
                   mean_children_per_couple=2.0):
    surnames, frequencies = load_native_surnames(native_file)
    pop = make_initial_population(surnames, frequencies, initial_pop_size)

    unique_counts = []
    total_pop_counts = []
    cumulative_surnames = set([p[0] for p in pop])

    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))

    for gen in range(generations):
        total_population = len(pop)
        unique_surnames = len(set(p[0] for p in pop))
        cumulative_surnames.update([p[0] for p in pop])

        total_pop_counts.append(total_population)
        unique_counts.append(unique_surnames)

        write_generation_log(
            generation_number=gen,
            total_population=total_population,
            unique_surnames=unique_surnames,
            cumulative_unique_surnames=len(cumulative_surnames)
        )

        write_surname_counts(pop, gen)

        ax.clear()
        ax.set_title("Unique Surnames and Population Over Generations")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Count")
        ax.plot(unique_counts, label="Unique Surnames", color='blue', marker='o')
        ax.plot(total_pop_counts, label="Total Population", color='red', marker='s')
        ax.legend()
        plt.pause(0.1)

        pop = reproduce_generation(pop, mean_children_per_couple=mean_children_per_couple)

        if len(pop) == 0:
            print(f"Population died out at generation {gen}")
            break

    plt.ioff()
    plt.show()

if __name__ == "__main__":
    run_simulation(
        native_file="surnames_sorted.csv",
        generations=50,
        initial_pop_size=10000,
        mean_children_per_couple=2.1
    )
