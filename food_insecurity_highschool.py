import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

# Load dataset
df = pd.read_csv('df_final.csv')  # Adjust path if needed

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
pdf = PdfPages('Food_Security_Report.pdf')

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

# Background density heatmap
sns.kdeplot(
    data=df, 
    x='ch_fi_rate_18', 
    y='percent_children_in_poverty', 
    fill=True, 
    thresh=0, 
    levels=100, 
    cmap="Blues", 
    alpha=0.3,
    ax=ax
)

# Scatter plot with updated mappings
scatter = sns.scatterplot(
    data=df,
    x='ch_fi_rate_18',
    y='percent_children_in_poverty',
    hue='median_household_income',         # Color by Median Household Income
    size='high_school_graduation_rate',     # Size by High School Graduation Rate
    palette='coolwarm_r',                      # Good for colorblind-friendly
    sizes=(80, 300),
    alpha=0.85,
    edgecolor='black',
    linewidth=0.7,
    ax=ax
)

# Dark regression line
sns.regplot(
    data=df,
    x='ch_fi_rate_18',
    y='percent_children_in_poverty',
    scatter=False,
    color='black',
    line_kws={"linewidth": 3, "linestyle": "dashed"},
    ax=ax
)

# Titles and labels
ax.set_title('Child Food Insecurity vs. Childhood Poverty', fontsize=18, weight='bold')
ax.set_xlabel('Child Food Insecurity Rate (%)', fontsize=13, weight='bold')
ax.set_ylabel('Percent of Children in Poverty (%)', fontsize=13, weight='bold')

# Updated subtitle
plt.suptitle(
    "Communities with higher child food insecurity face greater poverty,\n"
    "lower household incomes, and lower high school graduation rates.",
    fontsize=13, 
    y=0.94, 
    color='dimgray'
)

# Adjust legend
scatter.legend(
    title='Median Household Income ($)\n(Size = HS Graduation Rate %)', 
    bbox_to_anchor=(1.05, 1), 
    loc='upper left', 
    borderaxespad=0,
    fontsize=10, 
    title_fontsize=11
)

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
lower high school graduation rates are disproportionately impacted, as indicated by smaller, darker points.

Urgency of Action
Child food insecurity is not just a symptom of poverty—it is a driver of long-term economic and health hardship.
Without immediate intervention, children facing food insecurity today are at greater risk of malnutrition, starvation,
poor educational outcomes, and reduced future earning potential. The physical and cognitive effects of inadequate
nutrition during childhood can permanently undermine a child's ability to succeed later in life, compounding the cycle
of poverty across generations.

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

print("✅ Food_Security_Report.pdf successfully created!")
