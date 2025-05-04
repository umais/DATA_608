import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from matplotlib.lines import Line2D

# Load dataset
df = pd.read_csv('df_final.csv')

# Clean and filter necessary columns
df = df.dropna(subset=[
    'ch_fi_rate_18', 
    'percent_children_in_poverty', 
    'percent_limited_access_to_healthy_foods', 
    'high_school_graduation_rate', 
    'percent_low_birthweight', 
    'median_household_income'
])

# Set style
sns.set(style='whitegrid', font_scale=1.2)

# Create a PDF to save the report
pdf = PdfPages('Food_Security_Report_Improved.pdf')

# ----------------- Cover Page -----------------
fig_cover, ax_cover = plt.subplots(figsize=(11, 8.5))
ax_cover.axis('off')
ax_cover.text(0.5, 0.7, 'Story - 6:', fontsize=28, weight='bold', ha='center')
ax_cover.text(0.5, 0.6, 'What Is The State of Food Security and Nutrition in the US', fontsize=22, ha='center')
ax_cover.text(0.5, 0.45, 'CLASS DATA 608', fontsize=18, ha='center')
ax_cover.text(0.5, 0.35, 'UMAIS SIDDIQUI', fontsize=18, ha='center')
pdf.savefig(fig_cover)
plt.close(fig_cover)

# ----------------- Chart Page -----------------
fig, ax = plt.subplots(figsize=(14, 8))

# Darker background density heatmap
sns.kdeplot(
    data=df, 
    x='percent_children_in_poverty', 
    y='ch_fi_rate_18', 
    fill=True, 
    thresh=0, 
    levels=100, 
    cmap="Blues",  # Still blue, but will boost alpha below
    alpha=0.6,  # Darker background
    ax=ax
)

# Scale circle sizes based on high school graduation rate
min_size = 100
max_size = 600
sizes = np.interp(df['high_school_graduation_rate'], 
                  (df['high_school_graduation_rate'].min(), df['high_school_graduation_rate'].max()), 
                  (min_size, max_size))

# Define 3 graduation rate buckets
def grad_bucket(rate):
    if rate <= 75:
        return 'Low'
    elif rate <= 85:
        return 'Medium'
    else:
        return 'High'

df['grad_bucket'] = df['high_school_graduation_rate'].apply(grad_bucket)

# Color-blind safe edge colors
colorblind_edge_colors = df['grad_bucket'].map({
    'Low': '#7b3294',   # Dark purple (safe)
    'Medium': '#fdb863', # Amber/Gold (high contrast)
    'High': '#1b9e77'    # Teal/Blue-green (safe)
})

# Scatter plot
scatter = ax.scatter(
    df['percent_children_in_poverty'], 
    df['ch_fi_rate_18'], 
    c=df['median_household_income'], 
    cmap='coolwarm_r', 
    norm=plt.Normalize(df['median_household_income'].min(), df['median_household_income'].max()),
    s=sizes, 
    alpha=0.85, 
    edgecolor=colorblind_edge_colors,
    linewidth=2.5  # Thicker edges for visibility
)

# Regression line
sns.regplot(
    data=df,
    x='percent_children_in_poverty',
    y='ch_fi_rate_18',
    scatter=False,
    color='black',
    line_kws={"linewidth": 3, "linestyle": "dashed"},
    ax=ax
)

# Titles and labels
ax.set_title('Child Food Insecurity vs. Childhood Poverty', fontsize=18, weight='bold')
ax.set_xlabel('Percent of Children in Poverty (%)', fontsize=13, weight='bold')
ax.set_ylabel('Child Food Insecurity Rate (%)', fontsize=13, weight='bold')

# Colorbar for household income
cbar = plt.colorbar(scatter, ax=ax, pad=0.02)
cbar.set_label('Median Household Income ($)', fontsize=11, weight='bold')

# Custom legend for graduation buckets
legend_elements = [
    Line2D([0], [0], marker='o', linestyle='None', label='Low (≤75%)', 
           markerfacecolor='none', markeredgecolor='#7b3294', 
           markersize=14, markeredgewidth=3),
    Line2D([0], [0], marker='o', linestyle='None', label='Medium (76-85%)', 
           markerfacecolor='none', markeredgecolor='#fdb863', 
           markersize=14, markeredgewidth=3),
    Line2D([0], [0], marker='o', linestyle='None', label='High (>85%)', 
           markerfacecolor='none', markeredgecolor='#1b9e77', 
           markersize=14, markeredgewidth=3)
]

# Add legend with slightly lighter gray background and no line through circles
legend = ax.legend(
    handles=legend_elements, 
    title='HS Graduation Rate', 
    loc='upper left',  # Moved to upper left
    bbox_to_anchor=(0, 1.05),  # Adjusted to above the chart
    fontsize=10, 
    title_fontsize=11,
    frameon=True,
)

# Set legend background to match chart background
legend.get_frame().set_facecolor('white')  # Set background to white (chart background color)
legend.get_frame().set_edgecolor('black')  # Black border

# Set legend text and title color to a darker tone for better visibility
for text in legend.get_texts():
    text.set_color("black")  # Darker text
legend.get_title().set_color("black")  # Darker title

# Layout adjustments
fig.subplots_adjust(top=0.88, bottom=0.15, left=0.08, right=0.8)
plt.tight_layout()
pdf.savefig(fig)
plt.close(fig)

# ----------------- Key Insights Page -----------------
fig_insights, ax_insights = plt.subplots(figsize=(11, 8.5))
ax_insights.axis('off')
insights_text = """
Key Insights
The chart reveals a strong, positive correlation between child food insecurity and childhood poverty:
as food insecurity rates rise, so do poverty rates. Communities with lower median household incomes and
lower high school graduation rates are disproportionately impacted. 

Graduation rates are bucketed as Low (≤75%), Medium (76-85%), and High (>85%):
- Purple edges highlight the lowest graduation regions
- Amber edges mark medium rates
- Teal edges show high performing areas.

Urgency of Action
Child food insecurity is not just a symptom of poverty—it is a driver of long-term economic and health hardship.
Without immediate intervention, children facing food insecurity today are at greater risk of malnutrition, starvation,
poor educational outcomes, and reduced future earning potential. 

Call to Action
Addressing child food insecurity aligns directly with the Senator’s priorities of promoting economic stability
and educational opportunity. By investing in policies that ensure children have consistent access to nutritious food,
we can break the cycle of poverty and secure a stronger, more equitable future for all Americans.
"""
ax_insights.text(0.5, 0.5, insights_text, fontsize=12, ha='center', va='center', wrap=True)
pdf.savefig(fig_insights)
plt.close(fig_insights)

# ----------------- Save and Close PDF -----------------
pdf.close()

print("Food_Security_Report_Improved.pdf successfully created!")
