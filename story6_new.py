import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ---------------------
# Load Food Insecurity Data (2023)
# ---------------------
food_df = pd.read_csv("dec23pub.csv")

# Filter and clean
food_df = food_df[['PRTAGE', 'HRFS12CX']].dropna()
food_df = food_df[food_df['PRTAGE'] < 18]  # Children only
food_df['insecure'] = food_df['HRFS12CX'].apply(lambda x: 1 if x in [2, 3, 4] else 0)

# Compute 2023 food insecurity rate
food_insecurity_2023 = food_df['insecure'].mean() * 100

print(food_insecurity_2023)

# ---------------------
# Load and clean Poverty Data
# ---------------------
poverty_df = pd.read_excel("tableA3_hist_pov_by_all_and_age.xlsx", skiprows=4)

# Clean and format
poverty_df = poverty_df[pd.to_numeric(poverty_df.iloc[:, 0], errors='coerce').notnull()]
poverty_df.iloc[:, 0] = poverty_df.iloc[:, 0].astype(int)
poverty_df = poverty_df.rename(columns={poverty_df.columns[0]: 'year'})
poverty_df = poverty_df.rename(columns={poverty_df.columns[6]: 'child_poverty_rate'})
poverty_df = poverty_df.dropna()

# Clean percentage values and convert to float
poverty_df['child_poverty_rate'] = (
    poverty_df['child_poverty_rate']
    .astype(str)
    .str.replace('%', '', regex=False)
    .str.strip()
)
poverty_df['child_poverty_rate'] = pd.to_numeric(poverty_df['child_poverty_rate'], errors='coerce')

# Get 2023 poverty rate
poverty_2023 = poverty_df[poverty_df['year'] == 2023]
if poverty_2023.empty:
    raise ValueError("2023 poverty data not found.")
child_poverty_rate_2023 = poverty_2023.iloc[0]['child_poverty_rate']

print(child_poverty_rate_2023)

# ---------------------
# Plot Single-Year Comparison (Bar Plot)
# ---------------------
comparison_df = pd.DataFrame({
    'Metric': ['Child Poverty Rate', 'Child Food Insecurity Rate'],
    'Rate (%)': [child_poverty_rate_2023, food_insecurity_2023]
})

#plt.figure(figsize=(8, 6))
#sns.barplot(data=comparison_df, x='Metric', y='Rate (%)', palette='muted')
#plt.title("Child Poverty vs. Food Insecurity Rate (2023)")
#plt.ylim(0, max(comparison_df['Rate (%)']) * 1.2)
#plt.ylabel("Rate (%)")
#plt.grid(axis='y', linestyle='--', alpha=0.7)
#plt.tight_layout()
#plt.show()
