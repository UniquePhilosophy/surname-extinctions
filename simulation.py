import csv
import random
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import os

def load_surnames_from_csv(file_path):
    surnames = []
    frequencies = []
    with open(file_path, newline='', encoding='windows-1252') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            surname = row['Name'].strip()
            freq = int(row['Frequency'])
            if freq > 0:
                surnames.append(surname)
                frequencies.append(freq)
    return surnames, frequencies

def make_initial_population(surnames, frequencies, pop_size):
    weights = np.array(frequencies) / np.sum(frequencies)
    people = []
    for _ in range(pop_size):
        surname = random.choices(surnames, weights=weights)[0]
        sex = random.choice(['m', 'f'])
        people.append((surname, sex))
    return people

def reproduce_generation(pop):
    males = [p for p in pop if p[1] == 'm']
    females = [p for p in pop if p[1] == 'f']
    random.shuffle(males)
    random.shuffle(females)
    num_pairs = int(min(len(males), len(females)))
    # num_pairs = int(min(len(males), len(females)) * 0.8)
    new_generation = []

    for i in range(num_pairs):
        father_surname = males[i][0]
        child1_sex = random.choice(['m', 'f'])
        new_generation.append((father_surname, child1_sex))
        if random.random() < 0.44:
            child2_sex = random.choice(['m', 'f'])
            new_generation.append((father_surname, child2_sex))

    return new_generation

def write_surname_counts(population, generation_number, output_dir="surname_snapshots"):
    os.makedirs(output_dir, exist_ok=True)
    counts = Counter([p[0] for p in population])
    filename = os.path.join(output_dir, f"generation_{generation_number:02d}.csv")
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Surname", "Count"])
        for surname, count in sorted(counts.items(), key=lambda x: -x[1]):
            writer.writerow([surname, count])

def run_simulation(surname_file, generations=50, initial_pop_size=10000):
    surnames, frequencies = load_surnames_from_csv(surname_file)
    pop = make_initial_population(surnames, frequencies, initial_pop_size)
    unique_counts = []

    plt.ion()
    fig, ax = plt.subplots()

    for gen in range(generations):
        total_population = len(pop)
        unique_surnames = len(set(p[0] for p in pop))
        unique_counts.append(unique_surnames)

        print(f"Generation {gen}: {total_population} people, {unique_surnames} unique surnames")

        # Write current surname counts to CSV
        write_surname_counts(pop, gen)

        # Plot live graph
        ax.clear()
        ax.set_title("Unique Surnames Over Generations")
        ax.set_xlabel("Generation")
        ax.set_ylabel("Unique Surnames")
        ax.plot(unique_counts, marker='o', color='blue')
        plt.pause(0.1)

        # Prepare next generation
        pop = reproduce_generation(pop)

    plt.ioff()
    plt.show()

if __name__ == "__main__":
    run_simulation("surnames.csv", generations=50, initial_pop_size=10000)
