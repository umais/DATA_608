# 📚 Import libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 🗂️ Load the dataset
df = pd.read_csv('df_final.csv')

# ✨ Group data by state and take the mean
df_state = df.groupby('state_name').agg({
    'percent_below_poverty': 'mean',
    'ch_fi_rate_18': 'mean'
}).reset_index()

# 🔍 Quick preview
print(df_state.head())

# 📈 Scatter plot: State Average Poverty vs Child Food Insecurity
plt.figure(figsize=(14, 8))
sns.regplot(
    data=df_state,
    x='percent_below_poverty', 
    y='ch_fi_rate_18',
    scatter_kws={'s':100, 'color':'blue', 'alpha':0.7},
    line_kws={'color':'red'}
)

# Annotate points with state names
for i in range(df_state.shape[0]):
    plt.text(
        df_state['percent_below_poverty'][i]+0.2, 
        df_state['ch_fi_rate_18'][i], 
        df_state['state_name'][i], 
        fontsize=9
    )

plt.title('State-Level Relationship between Poverty and Child Food Insecurity', fontsize=18)
plt.xlabel('Average Percent Below Poverty Line (%)', fontsize=14)
plt.ylabel('Average Child Food Insecurity Rate (%)', fontsize=14)
plt.grid(True)
plt.tight_layout()
plt.show()
