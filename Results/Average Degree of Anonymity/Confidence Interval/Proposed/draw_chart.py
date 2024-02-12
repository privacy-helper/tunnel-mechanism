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
        confidence_interval, _ = calculate_confidence_interval(data[1:], confidence=confidence_level)
        label = 'Number of permanent relays per cluster = 10'
        if(i == 1):
            label = 'Number of permanent relays per cluster = 20'
        elif(i == 2):
            label = 'Number of permanent relays per cluster = 30'
        elif(i == 3):
            label = 'Number of permanent relays per cluster = 40'
        elif(i == 4):
            label = 'Number of permanent relays per cluster = 50'
        elif(i == 5):
            label = 'Number of clusters = 4'
        elif(i == 6):
            label = 'Number of clusters = 8'
        elif(i == 7):
            label = 'Number of clusters = 12'
        elif(i == 8):
            label = 'Number of clusters = 16'
        elif(i == 9):
            label = 'Number of clusters = 20'
            
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
                'Proposed_PR_Impact_2.xlsx', 
                'Proposed_PR_Impact_4.xlsx', 
                'Proposed_PR_Impact_6.xlsx', 
                'Proposed_PR_Impact_8.xlsx', 
                'Proposed_PR_Impact_10.xlsx', 
                'Proposed_Cluster_Impact_2.xlsx',
                'Proposed_Cluster_Impact_4.xlsx',
                'Proposed_Cluster_Impact_6.xlsx',
                'Proposed_Cluster_Impact_8.xlsx',
                'Proposed_Cluster_Impact_10.xlsx',
              ]
all_data = analyze_data(excel_files)
confidence_level = 0.95
output_image = 'output.png'
plot_data_with_confidence_interval(all_data, confidence_level, output_image)

print(f"Confidence Level: {confidence_level * 100}%")
