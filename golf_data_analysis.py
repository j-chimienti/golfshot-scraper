import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure plots
sns.set(style="whitegrid")

# Load golf data from a CSV file
def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        print(f"Data loaded successfully from {file_path}")
        return data
    except FileNotFoundError:
        print("File not found! Please check the path and try again.")
        return None

# Analyze stats
def analyze_data(data):
    # Example columns: Date, Fairways Hit, Greens in Regulation, Putts, Penalty Strokes, Score
    print("\n--- Basic Overview ---")
    print(data.describe())  # Show statistical summary of numeric columns
    print("\n--- Column Names ---")
    print(data.columns)     # Show all column names

    # Average statistics
    avg_score = data['Score'].mean()
    avg_putts = data['Putts'].mean()
    avg_penalty_strokes = data['Penalty Strokes'].mean()
    avg_fairways = data['Fairways Hit (%)'].mean()
    avg_gir = data['Greens in Regulation (%)'].mean()

    print("\n--- Average Stats ---")
    print(f"Average Score: {avg_score:.2f}")
    print(f"Average Putts per Round: {avg_putts:.2f}")
    print(f"Average Penalty Strokes per Round: {avg_penalty_strokes:.2f}")
    print(f"Fairways Hit (%): {avg_fairways:.2f}")
    print(f"Greens in Regulation (%): {avg_gir:.2f}")

# Visualize data
def visualize_data(data):
    # Scatter plot: Score vs. Greens in Regulation
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Greens (%)', y score)