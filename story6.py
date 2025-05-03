import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load your dataset (replace with your actual filename)
df = pd.read_csv('dec23pub.csv')

# Rename the relevant columns if needed
age_col = 'PRTAGE'         # Age of individual
gender_col = 'PESEX'       # 1 = Male, 2 = Female
state_col = 'GESTFIPS'     # State FIPS code
food_security_col = 'HRFS12CX'  # Food security (12-month)

# Drop rows with missing relevant data
df = df[[age_col, gender_col, state_col, food_security_col]].dropna()

# Filter only valid ages
df = df[df[age_col] < 100]

# Define age group and gender labels
df['age_group'] = df[age_col].apply(lambda x: 'Child' if x < 18 else 'Adult')
df['gender_group'] = df[gender_col].map({1: 'Male', 2: 'Female'})

# Optional: Define a child gender group to split children from men/women
df['gender_age'] = df.apply(
    lambda x: 'Child' if x['age_group'] == 'Child' else x['gender_group'], axis=1
)

# Classify food security status (1=secure, 2-4=insecure)
df['insecure'] = df[food_security_col].apply(lambda x: 1 if x in [2, 3, 4] else 0)

# Map state FIPS codes to state names
import us  # You may need to install with: pip install us
state_map = {state.fips: state.name for state in us.states.STATES}
df['state'] = df[state_col].astype(str).str.zfill(2).map(state_map)

# Group and calculate food insecurity rate
grouped = df.groupby(['state', 'gender_age'])['insecure'].mean().reset_index()
grouped['insecure'] *= 100  # Convert to percentage

# Pivot to get heatmap format
heatmap_data = grouped.pivot(index='state', columns='gender_age', values='insecure').fillna(0)

# Plot the heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(heatmap_data, cmap='coolwarm', annot=True, fmt=".1f", linewidths=0.5)
plt.title('Food Insecurity Rates by State, Gender, and Age Group (%)')
plt.ylabel('State')
plt.xlabel('Demographic Group')
plt.tight_layout()
plt.show()
