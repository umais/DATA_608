import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

# Load the data from the uploaded Excel file
file_path = 'DataRolesSalary.xlsx'  # Update this with the actual Excel file path
# Assuming the Excel file has a sheet named 'Sheet1'
data = pd.read_excel(file_path, sheet_name='Sheet1')

# Data cleaning: Removing '$' and ',' from the 'Average Salary' column and converting it to numeric
data['Average Salary'] = data['Average Salary'].replace({'\$': '', ',': ''}, regex=True).astype(float)

# Pivoting data for combined chart
pivot_data = data.pivot_table(index='State', columns='Title', values='Average Salary')

# Define a colorblind-friendly palette (Color Universal Design) for markers
colors = ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7', '#999999']

# Plotting a combined chart with bars and markers (no lines)
fig, ax1 = plt.subplots(figsize=(14, 7))  # Increase figure size for better readability

# Lighter bar color with no borders
bar_color = '#D3D3D3'  # Light gray color for bars (no border)

# List to store the marker plot handles for the legend
markers = []

# Loop over each role in the pivot data
for i, role in enumerate(pivot_data.columns):
    # Plot bars for each role with the same light color
    ax1.bar(pivot_data.index, pivot_data[role], color=bar_color, alpha=0.7, label=role)  # Bars with light color

    # Add markers on top of the bars for each role (as scatter plot)
    scatter = ax1.scatter(pivot_data.index, pivot_data[role], color=colors[i % len(colors)], marker='o', zorder=5, s=120, edgecolor='black', label=role)
    
    # Append scatter objects to the markers list for the legend
    markers.append(scatter)

# Adding labels and improving visibility
ax1.set_xlabel('State', fontsize=14)
ax1.set_ylabel('Average Salary', fontsize=14)
plt.xticks(rotation=90, fontsize=12)  # Larger x-tick labels for readability
plt.yticks(fontsize=12)
plt.title('Average Salary for Data Practitioner by Role and State', fontsize=16, fontweight='bold')

# Adding grid lines for better salary comparison
ax1.yaxis.grid(True, linestyle='--', alpha=0.6)

# Calculate national highest, lowest, and median salary for each role
highest_salaries = pivot_data.max()
lowest_salaries = pivot_data.min()
median_salaries = pivot_data.median()

# Add annotations for the national highest salary per role (in front of bars)
for i, role in enumerate(pivot_data.columns):
    max_salary = pivot_data[role].max()
    max_state = pivot_data[role].idxmax()
    ax1.annotate(f'{int(max_salary)}', xy=(max_state, max_salary), xytext=(5, 5), textcoords='offset points',
                 arrowprops=dict(arrowstyle="->", lw=1.5), fontsize=12, color='black', zorder=10)  # Bring annotations to the front

# Plot horizontal lines for national highest, lowest, and median salary for each role
national_markers = []
for i, role in enumerate(pivot_data.columns):
    # Plot horizontal lines and include salary values in the label
    ax1.axhline(y=highest_salaries[role], color=colors[i % len(colors)], linestyle='-', linewidth=2, alpha=0.8, zorder=2)
    ax1.axhline(y=lowest_salaries[role], color=colors[i % len(colors)], linestyle=':', linewidth=2, alpha=0.8, zorder=2)
    ax1.axhline(y=median_salaries[role], color=colors[i % len(colors)], linestyle='--', linewidth=2, alpha=0.8, zorder=2)

    # Append dummy handles for the second legend with salary values
    national_markers.append(plt.Line2D([0], [0], color=colors[i % len(colors)], lw=2, linestyle='-', 
                                       label=f'Highest ({role}): ${int(highest_salaries[role]):,}'))
    national_markers.append(plt.Line2D([0], [0], color=colors[i % len(colors)], lw=2, linestyle=':', 
                                       label=f'Lowest ({role}): ${int(lowest_salaries[role]):,}'))
    national_markers.append(plt.Line2D([0], [0], color=colors[i % len(colors)], lw=2, linestyle='--', 
                                       label=f'Median ({role}): ${int(median_salaries[role]):,}'))

# **Explicitly create the first legend for scatter plots (markers)**
first_legend = ax1.legend(handles=markers, loc='upper left', fontsize=10, title='Roles', bbox_to_anchor=(1.05, 1), borderaxespad=0.)
ax1.add_artist(first_legend)  # Explicitly add the first legend

# Add a second legend for national statistics (highest, lowest, median) on the side, including the actual salary values
plt.legend(handles=national_markers, loc='lower left', fontsize=10, title='National Stats', bbox_to_anchor=(1.05, 0), borderaxespad=0.)

# Adding a tight layout to prevent overlap
plt.tight_layout()

# Save the figure
chart_path = 'salary_visualization_with_salary_values_in_legend.png'
plt.savefig(chart_path, dpi=300)

# Observations text
observations = """
Observations:
1. The salary levels for different roles vary significantly across states.
2. The Data Analyst roles generally show consistent salaries across most states.
3. There is a clear contrast in salaries between Data Engineer and Business Analyst roles.
4. Some states show considerably higher salaries for specific roles, indicating regional salary disparities.
"""

# Generate a PDF including the chart and observations
pdf_path = 'Story4_Umais_Siddiqui.pdf'
with PdfPages(pdf_path) as pdf:
    # Add the chart to the PDF
    pdf.savefig(fig)
    # Create a new page for the observations
    plt.figure(figsize=(8, 6))
    plt.text(0.1, 0.8, observations, fontsize=12, wrap=True, ha='left')
    plt.axis('off')
    pdf.savefig()
    plt.close()

# Show the chart
plt.show()
