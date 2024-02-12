import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def calculate_confidence_interval(data, confidence=0.95):
    mean = np.mean(data)
    std_error = stats.sem(data)
    margin_of_error = std_error * stats.t.ppf((1 + confidence) / 2, len(data) - 1)
    confidence_interval = (mean - margin_of_error, mean + margin_of_error)
    confidence_level = confidence * 100

    return confidence_interval, confidence_level

def analyze_data(excel_files, sheet_name='Sheet1'):
    all_data = []

    for excel_file in excel_files:
        df = pd.read_excel(excel_file, sheet_name)
        all_data.append(df.values.flatten())

    return all_data

def plot_data_with_confidence_interval(all_data, confidence_level, output_image='output.png'):
    num_datasets = len(all_data)

    plt.figure(figsize=(12, 8))

    for i, data in enumerate(all_data):
        # print(data[1:])
        confidence_interval, _ = calculate_confidence_interval(data[1:], confidence=confidence_level)
        label = 'TOR'
        if(i == 1):
            label = 'I2P'
        if(i == 2):
            label = 'Proposed'
            
        plt.hist(data[1:], bins=10, alpha=0.5, label=label)

        # Plot confidence interval
        plt.axvline(x=confidence_interval[0], linestyle='--', color=f'C{i}', label=f'CI {label}')
        plt.axvline(x=confidence_interval[1], linestyle='--', color=f'C{i}')

    plt.title(f'Data Distributions with {confidence_level}% Confidence Intervals')
    plt.xlabel('Delay (Seconds)')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True)
    plt.savefig(output_image)
    plt.show()

# Example usage:
max_delay_time_in_ms = 60      # {25, 50, 75, 100}
excel_files = [
                'test_TOR_' + str(max_delay_time_in_ms) + '.xlsx', 
                'test_I2P_' + str(max_delay_time_in_ms) + '.xlsx', 
                'test_Proposed_' + str(max_delay_time_in_ms) + '.xlsx'
              ]
all_data = analyze_data(excel_files)
confidence_level = 0.95
output_image = 'delay_' + str(max_delay_time_in_ms) + '.png'
plot_data_with_confidence_interval(all_data, confidence_level, output_image)

print(f"Confidence Level: {confidence_level * 100}%")
