import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import os
from scipy import stats
from matplotlib.backends.backend_pdf import PdfPages
import warnings

warnings.filterwarnings('ignore')
sns.set(style="whitegrid")
plt.rcParams.update({'font.size': 12})

def add_speaker_notes(notes):
    plt.figtext(0.5, 0.03, f"Speaker Notes: {notes}", fontsize=10, ha='center',
                wrap=True, va='center',
                bbox=dict(facecolor='lightyellow', alpha=0.8, boxstyle='round,pad=0.8',
                          edgecolor='goldenrod', linewidth=2),
                weight='bold', color='black',
                transform=plt.gcf().transFigure,
                linespacing=1.5)

def fetch_temperature_data():
    url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
    df = pd.read_csv(url, skiprows=1)
    df = df[['Year', 'J-D']].rename(columns={'J-D': 'Anomaly'})
    df['Anomaly'] = pd.to_numeric(df['Anomaly'], errors='coerce')
    return df.dropna()[df['Year'] >= 1995]

def fetch_hurricane_data():
    url = "https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2022-050423.txt"
    r = requests.get(url)
    lines = r.text.splitlines()

    yearly_data = {}
    current_year, max_wind = None, 0

    for line in lines:
        if line[:2].isalpha():
            if current_year and max_wind >= 64:
                yearly_data.setdefault(current_year, []).append(max_wind)
            current_year = int(line.split(',')[0][-4:])
            max_wind = 0
        else:
            try:
                wind = int(line.split(',')[6].strip())
                max_wind = max(max_wind, wind)
            except:
                continue

    if current_year and max_wind >= 64:
        yearly_data.setdefault(current_year, []).append(max_wind)

    data = []
    for year in range(1995, 2023):
        winds = yearly_data.get(year, [])
        total = len(winds)
        major = sum(1 for w in winds if w >= 96)
        avg_wind = np.mean(winds) if winds else 0
        data.append([year, total, major, avg_wind])
    return pd.DataFrame(data, columns=['Year', 'Total_Hurricanes', 'Major_Hurricanes', 'Avg_Max_Wind'])

def analyze(temp, hurricane):
    merged = pd.merge(temp, hurricane, on='Year')
    results = {'merged': merged, 'cor': {}, 'reg': {}}
    for col in ['Total_Hurricanes', 'Major_Hurricanes', 'Avg_Max_Wind']:
        x, y = merged['Anomaly'], merged[col]
        results['cor'][col] = stats.pearsonr(x, y)
        results['reg'][col] = stats.linregress(x, y)
    return results

def slide_intro(pdf):
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.axis('off')
    ax.set_facecolor('#f0f8ff')
    plt.text(0.5, 0.8, "🌎 Climate Change & Hurricanes 🌀", fontsize=28, ha='center', weight='bold', color='#003366')
    plt.text(0.5, 0.65, "Are warmer oceans fueling stronger storms?", fontsize=20, ha='center', color='#1170aa')
    plt.text(0.5, 0.5, "DATA 608 - Story 5 Presentation", fontsize=16, ha='center', color='#444444')
    plt.text(0.5, 0.35, "By: UMAIS SIDDIQUI", fontsize=16, ha='center', weight='bold', color='#222222')
    add_speaker_notes("Today we'll explore the connection between global warming and hurricane activity. We'll ask: Are rising temperatures linked to more or stronger storms?")
    pdf.savefig()
    plt.close()

def slide_combined_temp_hurricanes(temp, hurricane, pdf):
    merged = pd.merge(temp, hurricane, on='Year')

    fig, ax1 = plt.subplots(figsize=(11, 8.5))
    ax1.set_facecolor('#f0f0f0')

    color1 = '#d95f02'
    ax1.plot(merged['Year'], merged['Anomaly'], color=color1, marker='o', linewidth=2, label='Temp Anomaly (°C)')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Temperature Anomaly (°C)', color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.axhline(0, color='gray', linestyle='--', linewidth=1)

    ax2 = ax1.twinx()
    color2 = '#1170aa'
    ax2.bar(merged['Year'], merged['Total_Hurricanes'], color=color2, alpha=0.6, label='Total Hurricanes')
    ax2.set_ylabel('Total Hurricanes', color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)

    fig.suptitle('🌡️ Temperature vs 🌀 Hurricane Frequency (1995–2022)', fontsize=20)
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.92), fontsize=12)

    add_speaker_notes("This chart shows global temperature anomalies and hurricane counts together from 1995 to 2022. It helps us see if hotter years had more hurricanes.")
    pdf.savefig()
    plt.close()

def slide_intensity_correlation(results, pdf):
    merged = results['merged']
    fig, ax = plt.subplots(figsize=(11, 8.5))
    scatter = ax.scatter(merged['Anomaly'], merged['Avg_Max_Wind'], c=merged['Year'], cmap='cividis', s=100, edgecolor='white')
    slope, intercept = results['reg']['Avg_Max_Wind'][0], results['reg']['Avg_Max_Wind'][1]
    x_vals = np.array([merged['Anomaly'].min(), merged['Anomaly'].max()])
    y_vals = intercept + slope * x_vals
    ax.plot(x_vals, y_vals, color='#d95f02', linewidth=3, linestyle='--', label='Trend')
    ax.set_title('💨 Temperature vs Hurricane Intensity')
    ax.set_xlabel('Temperature Anomaly (°C)')
    ax.set_ylabel('Avg Max Wind Speed (knots)')
    cbar = plt.colorbar(scatter)
    cbar.set_label('Year')
    ax.legend()
    add_speaker_notes("This scatter plot looks at hurricane intensity vs temperature anomaly. Each point is a year, and we see if hotter years had stronger average winds.")
    pdf.savefig()
    plt.close()

def slide_summary(results, pdf):
    merged = results['merged']
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.axis('off')
    ax.set_facecolor('#f9f9f9')
    ax.set_title("📊 Summary & Key Takeaways", fontsize=24, weight='bold', color='#003366')
    lines = [
        f"• Temp ↔ Total Hurricanes: r = {results['cor']['Total_Hurricanes'][0]:.2f}",
        f"• Temp ↔ Major Hurricanes: r = {results['cor']['Major_Hurricanes'][0]:.2f}",
        f"• Temp ↔ Avg Wind Speed: r = {results['cor']['Avg_Max_Wind'][0]:.2f}"
    ]
    for i, line in enumerate(lines):
        ax.text(0.1, 0.7 - i*0.1, line, fontsize=16, ha='left', color='#333')
    ax.text(0.1, 0.3, "Conclusion:", fontsize=18, weight='bold', color='#003366')
    ax.text(0.1, 0.23, "There is evidence that warmer years may be linked to more and stronger hurricanes.",
            fontsize=14, ha='left', color='#333')
    ax.text(0.1, 0.18, "This relationship is important for disaster planning and climate policy.",
            fontsize=14, ha='left', color='#333')
    add_speaker_notes("These results suggest a link between warming and more intense hurricanes, but further study is needed. These trends matter for climate action and public safety.")
    pdf.savefig()
    plt.close()

def main():
    os.makedirs('output', exist_ok=True)
    temp = fetch_temperature_data()
    hurricane = fetch_hurricane_data()
    results = analyze(temp, hurricane)
    with PdfPages("output/climate_impact_presentation.pdf") as pdf:
        slide_intro(pdf)
        slide_combined_temp_hurricanes(temp, hurricane, pdf)
        slide_intensity_correlation(results, pdf)
        slide_summary(results, pdf)

if __name__ == "__main__":
    main()
