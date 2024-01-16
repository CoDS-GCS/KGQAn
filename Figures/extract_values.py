import csv
import pandas as pd

def read_values_from_file():
    benchmark_to_values = dict()
    file = 'src/evaluation/output/evaluation_results.csv'
    with open(file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        rows = list(csv_reader)

        for i in range(0, len(rows), 3):
            current_benchmark = rows[i][0] if i < len(rows) else None
            current_values = rows[i + 2] if i + 2 < len(rows) else None
            values = [float(value) for value in current_values]

            if current_benchmark and current_values:
                benchmark_to_values[current_benchmark] = values

    return benchmark_to_values

def get_response_time_per_benchmark():
    file = 'src/evaluation/output/evaluation_response_time.csv'
    df = pd.read_csv(file)
    return df


