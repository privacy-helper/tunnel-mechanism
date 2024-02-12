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
        print(df.values)
        all_data.append(df.values[9].flatten())

    return all_data

def plot_data_with_confidence_interval(all_data, confidence_level, output_image='output.png'):
    num_datasets = len(all_data)

    plt.figure(figsize=(12, 8))
    plt.rcParams.update({'font.size': 10})
    plt.rcParams.update({'font.weight': 'bold'})
    plt.rcParams["font.family"] = "Times New Roman"

    for i, data in enumerate(all_data):
        # print(data[1:])
        confidence_interval, _ = calculate_confidence_interval(data[1:], confidence=confidence_level)
        label = 'TOR (Concurrent tunnel-build rate = 0.1)'
        if(i == 1):
            label = 'TOR (Concurrent tunnel-build rate = 0.5)'
        elif(i == 2):
            label = 'TOR (Concurrent tunnel-build rate = 1)'
        elif(i == 3):
            label = 'I2P (Concurrent tunnel-build rate = 0.1)'
        elif(i == 4):
            label = 'I2P (Concurrent tunnel-build rate = 0.5)'
        elif(i == 5):
            label = 'I2P (Concurrent tunnel-build rate = 1)'
        elif(i == 6):
            label = 'Proposed structure (Permanent relays per cluster = 1)'
        elif(i == 7):
            label = 'Proposed structure (Permanent relays per cluster = 5)'
        elif(i == 8):
            label = 'Proposed structure (Permanent relays per cluster = 10)'
        elif(i == 9):
            label = 'Proposed structure (Permanent relays per cluster = 25)'
            
        plt.hist(data[1:], bins=10, alpha=0.5, label=label)

        # Plot confidence interval
        plt.axvline(x=confidence_interval[0], linestyle='--', color=f'C{i}', label=f'CI {label}')
        plt.axvline(x=confidence_interval[1], linestyle='--', color=f'C{i}')

    plt.title(f'Data Distributions with {confidence_level}% Confidence Intervals', fontdict={'fontsize': 13, 'fontweight': 'bold'})
    plt.xlabel('Average Degree of Anonymity', fontdict={'fontsize': 13, 'fontweight': 'bold'})
    plt.ylabel('Frequency', fontdict={'fontsize': 13, 'fontweight': 'bold'})
    plt.legend()
    plt.grid(True)
    plt.savefig(output_image)
    plt.show()

# Example usage:
excel_files = [
                'Com_TOR_0.1.xlsx', 
                'Com_TOR_0.5.xlsx',
                'Com_TOR_1.xlsx',
                'Com_I2P_0.1.xlsx', 
                'Com_I2P_0.5.xlsx',
                'Com_I2P_1.xlsx',
                'Com_Proposed_1.xlsx',
                'Com_Proposed_5.xlsx',
                'Com_Proposed_10.xlsx',
                'Com_Proposed_25.xlsx',
              ]
all_data = analyze_data(excel_files)
confidence_level = 0.95
output_image = 'output.png'
plot_data_with_confidence_interval(all_data, confidence_level, output_image)

print(f"Confidence Level: {confidence_level * 100}%")
