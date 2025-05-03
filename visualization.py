import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Create the dataset
data = {
    "Employee ID": list(range(1, 21)),
    "Pre-Training": [65, 70, 55, 68, 77, 62, 55, 80, 78, 69, 60, 67, 71, 55, 73, 64, 68, 75, 66, 70],
    "Post-Training": [72, 85, 60, 75, 80, 65, 50, 90, 82, 74, 62, 70, 75, 58, 78, 70, 72, 77, 68, 76]
}

df = pd.DataFrame(data)

# Set up the plot
plt.figure(figsize=(14, 7))
sns.set_style("whitegrid")

# Melt the DataFrame for seaborn compatibility
df_melted = df.melt(id_vars="Employee ID", value_vars=["Pre-Training", "Post-Training"],
                    var_name="Training Stage", value_name="Productivity Score")

# Create line plot
sns.lineplot(data=df_melted, x="Employee ID", y="Productivity Score", hue="Training Stage", marker="o", linewidth=2.5)

# Highlight declines with red lines
for i, (pre, post) in enumerate(zip(df["Pre-Training"], df["Post-Training"])):
    if post < pre:
        plt.plot([i+1, i+1], [pre, post], color='red', linewidth=3)

# Titles and labels
plt.title("Employee Productivity Before and After Training", fontsize=18, weight='bold')
plt.xlabel("Employee ID", fontsize=12)
plt.ylabel("Productivity Score", fontsize=12)
plt.xticks(df["Employee ID"])
plt.legend(title="Training Stage")
plt.tight_layout()

# Save the plot as a PNG
plt.savefig("training_productivity_visual.png", dpi=300)
plt.show()
