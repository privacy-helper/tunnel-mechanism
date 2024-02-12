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
        # label = 'Type_One_ACT_0.5'
        # if(i == 1):
            # label = 'Type_Two_ACT_0.5'
        # elif(i == 2):
            # label = 'Type_Two_TBC_0.5'
            
        label = 'Active tunnels rate = 0.5'
        if(i == 1):
            label = 'Concurrent tunnel-build rate = 0.5'
            
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
                # 'Type_One_ACT_5.xlsx', 
                'Type_Two_ACT_5.xlsx',
                'Type_Two_TBC_5.xlsx',
              ]
all_data = analyze_data(excel_files)
confidence_level = 0.95
output_image = 'output.png'
plot_data_with_confidence_interval(all_data, confidence_level, output_image)

print(f"Confidence Level: {confidence_level * 100}%")
