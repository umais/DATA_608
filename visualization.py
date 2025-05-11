import pandas as pd
import plotly.express as px
import os

# Sample dataset from plotly (can be replaced with any time series data)
url = 'https://raw.githubusercontent.com/plotly/datasets/master/2011_us_ag_exports.csv'
data = pd.read_csv(url)

# Simulating a time series dataset by expanding the dataset with dummy months
import numpy as np

states = data['state'].unique()
months = pd.date_range(start="2021-01-01", periods=12, freq='M').strftime('%Y-%m')

df_list = []
for month in months:
    temp = data.copy()
    temp['month'] = month
    temp['unemployment_rate'] = np.random.uniform(3, 12, len(temp))  # Random unemployment rate
    df_list.append(temp)

df = pd.concat(df_list)

# Create interactive line plot
fig = px.line(df,
              x='month',
              y='unemployment_rate',
              color='state',
              line_group='state',
              hover_name='state',
              title='Monthly Unemployment Rate by State',
              labels={'month': 'Month', 'unemployment_rate': 'Unemployment Rate (%)'})

fig.update_layout(
    xaxis=dict(rangeslider_visible=True),
    legend_title_text='State'
)

# Save the interactive chart as an HTML file in docs/index.html
os.makedirs("docs", exist_ok=True)
fig.write_html("docs/visualization.html")

print("✅ Visualization created: docs/visualization.html")
