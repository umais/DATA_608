import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import os
from scipy import stats
import warnings
from matplotlib.backends.backend_pdf import PdfPages

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
    print(f"Speaker Notes: {notes}")

def fetch_temperature_data():
    url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
    try:
        df = pd.read_csv(url, skiprows=1)
        df = df[['Year', 'J-D']].rename(columns={'J-D': 'Anomaly'})
        df['Anomaly'] = pd.to_numeric(df['Anomaly'], errors='coerce')
        return df.dropna()[df['Year'] >= 1995]
    except:
        raise RuntimeError("Failed to fetch temperature data")

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
    plt.text(0.5, 0.65, "Exploring Temperature and Hurricane Trends (1995–2022)", fontsize=20, ha='center', color='#1170aa')
    plt.text(0.5, 0.5, "DATA 608 - Story 5 Presentation", fontsize=16, ha='center', color='#444444')
    plt.text(0.5, 0.35, "By: UMAIS SIDDIQUI", fontsize=16, ha='center', weight='bold', color='#222222')
    add_speaker_notes("Today we'll explore the relationship between global warming and hurricane activity. Our goal is to understand if rising temperatures affect hurricane frequency and intensity using real-world data.")
    pdf.savefig()
    plt.close()

def slide_temperature_trend(data, pdf):
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.set_facecolor('#f8f9fa')
    norm = plt.Normalize(data['Anomaly'].min(), data['Anomaly'].max())
    colors = plt.cm.coolwarm(norm(data['Anomaly']))
    ax.scatter(data['Year'], data['Anomaly'], s=100, c=colors, edgecolor='white', linewidth=1.5)
    slope, intercept = np.polyfit(data['Year'], data['Anomaly'], 1)
    ax.plot(data['Year'], slope * data['Year'] + intercept, color='#d95f02', linewidth=3, linestyle='--')
    ax.axhline(0, color='#555', linestyle='--', alpha=0.7)
    ax.set_title('🌡️ Global Temperature Anomalies', fontsize=22)
    ax.set_xlabel('Year')
    ax.set_ylabel('Anomaly (°C)')
    add_speaker_notes("This graph shows how global temperature has changed from 1995 to 2022. The dashed trend line indicates a warming trend over this period, with anomalies getting higher over time.")
    pdf.savefig()
    plt.close()

def slide_hurricane_trend(data, pdf):
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.set_facecolor('whitesmoke')
    x = np.arange(len(data['Year']))
    width = 0.4
    ax.bar(x - width/2, data['Total_Hurricanes'], width, label='Total', color='#1170aa')
    ax.bar(x + width/2, data['Major_Hurricanes'], width, label='Major', color='#fc7d0b')
    ax.set_xticks(x)
    ax.set_xticklabels(data['Year'], rotation=45)
    ax.set_title('🌀 Hurricane Counts per Year')
    ax.set_ylabel('Count')
    ax.set_xlabel('Year')
    ax.legend()
    add_speaker_notes("This bar chart shows the number of total and major hurricanes each year. Major hurricanes are Category 3 and above, with wind speeds over 96 knots.")
    pdf.savefig()
    plt.close()

def slide_correlation(results, pdf):
    merged = results['merged']
    fig, ax = plt.subplots(figsize=(11, 8.5))
    scatter = ax.scatter(merged['Anomaly'], merged['Total_Hurricanes'], c=merged['Year'], cmap='cividis', s=100, edgecolor='white')
    slope, intercept = results['reg']['Total_Hurricanes'][0], results['reg']['Total_Hurricanes'][1]
    x_vals = np.array([merged['Anomaly'].min(), merged['Anomaly'].max()])
    y_vals = intercept + slope * x_vals
    ax.plot(x_vals, y_vals, color='#d95f02', linewidth=3, linestyle='--', label='Trend')
    ax.set_title('🌡️ Temp vs Hurricane Frequency')
    ax.set_xlabel('Temperature Anomaly')
    ax.set_ylabel('Hurricane Count')
    cbar = plt.colorbar(scatter)
    cbar.set_label('Year')
    ax.legend()
    add_speaker_notes("This scatter plot explores whether years with higher global temperatures had more hurricanes. The trend line helps show if there's any overall relationship.")
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
    ax.set_title('💨 Temp vs Hurricane Intensity')
    ax.set_xlabel('Temperature Anomaly')
    ax.set_ylabel('Avg Max Wind (knots)')
    cbar = plt.colorbar(scatter)
    cbar.set_label('Year')
    ax.legend()
    add_speaker_notes("Here we look at whether global temperature affects hurricane strength. Each dot represents a year, and we plot the average max wind speed of hurricanes against temperature anomaly.")
    pdf.savefig()
    plt.close()

def slide_summary(results, pdf):
    merged = results['merged']
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.axis('off')
    ax.set_facecolor('#f9f9f9')
    ax.set_title("📊 Summary & Insights", fontsize=24, weight='bold', color='#003366')
    lines = [
        f"• Temp ↔ Total Hurricanes: r={results['cor']['Total_Hurricanes'][0]:.2f}",
        f"• Temp ↔ Major Hurricanes: r={results['cor']['Major_Hurricanes'][0]:.2f}",
        f"• Temp ↔ Avg Wind Speed: r={results['cor']['Avg_Max_Wind'][0]:.2f}"
    ]
    for i, line in enumerate(lines):
        ax.text(0.1, 0.7 - i*0.1, line, fontsize=16, ha='left', color='#333')
    ax.text(0.1, 0.3, "Conclusion:", fontsize=18, weight='bold', color='#003366')
    ax.text(0.1, 0.23, "There is measurable correlation between warming and hurricane behavior.",
            fontsize=14, ha='left', color='#333')
    ax.text(0.1, 0.18, "Further research is essential for stronger conclusions.",
            fontsize=14, ha='left', color='#333')
    add_speaker_notes("This summary slide highlights the key findings of our analysis. There are positive correlations between rising temperatures and hurricane frequency and intensity, though causation cannot be assumed without deeper study.")
    pdf.savefig()
    plt.close()

def main():
    os.makedirs('output', exist_ok=True)
    temp = fetch_temperature_data()
    hurricane = fetch_hurricane_data()
    results = analyze(temp, hurricane)
    with PdfPages("output/climate_analysis_full.pdf") as pdf:
        slide_intro(pdf)
        slide_temperature_trend(temp, pdf)
        slide_hurricane_trend(hurricane, pdf)
        slide_correlation(results, pdf)
        slide_intensity_correlation(results, pdf)
        slide_summary(results, pdf)

if __name__ == "__main__":
    main()