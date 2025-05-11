import os
import pandas as pd
import geopandas as gpd
import folium
from folium.features import DivIcon, GeoJsonTooltip, Popup
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import base64
from io import BytesIO

# === Load US States GeoJSON ===
us_states = gpd.read_file("https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json")

# === Load Consumption Data ===
consumption_df = pd.read_csv("energy_indicators.csv")
consumption_df['abbreviation'] = consumption_df['State'].str.strip().str.upper()
consumption_df = consumption_df[~consumption_df['abbreviation'].str.contains('TOTAL', case=False, na=False)]
consumption_df = consumption_df[~consumption_df['abbreviation'].isin(['US', 'TOTAL US'])]
consumption_df['2022'] = consumption_df['2022'].astype(str).str.replace(',', '', regex=False).astype(float)
consumption_2022 = consumption_df.groupby('abbreviation').agg({'2022': 'sum'}).reset_index().rename(columns={'2022': 'consumption'})

# === Load Energy Production Data ===
energy_df = pd.read_csv("Energy_Production.csv")
energy_df = energy_df[['State', 'MSN', '2022']]
msn_to_type = {
    'CLPRB': 'Coal', 'CLPRK': 'Coal', 'CLPRP': 'Coal',
    'NGMPB': 'Natural Gas', 'NGMPK': 'Natural Gas', 'NGMPP': 'Natural Gas',
    'NUEGP': 'Nuclear', 'NUETB': 'Nuclear',
    'WYTCB': 'Wind',
    'SOTCB': 'Solar', 'SOPTCB': 'Solar'
}
energy_df['Energy_Type'] = energy_df['MSN'].map(msn_to_type)
energy_df = energy_df[energy_df['Energy_Type'].notna()]
energy_df['abbreviation'] = energy_df['State'].str.strip().str.upper()
energy_df['2022'] = energy_df['2022'].astype(str).str.replace(',', '', regex=False).astype(float)

# === Aggregate
energy_breakdown = energy_df.groupby(['abbreviation', 'Energy_Type']).agg({'2022': 'sum'}).reset_index()
energy_pivot = energy_breakdown.pivot(index='abbreviation', columns='Energy_Type', values='2022').reset_index().fillna(0)
energy_pivot['total_production'] = energy_pivot[['Coal', 'Natural Gas', 'Nuclear', 'Wind', 'Solar']].sum(axis=1)

# === Merge with consumption
state_data = pd.merge(consumption_2022, energy_pivot, on='abbreviation', how='left')
state_data['vulnerability_score'] = round(
    (state_data['consumption'] - state_data['total_production']) / state_data['consumption'], 2)
state_data['vulnerability_score'] = state_data['vulnerability_score'].clip(lower=0).fillna(0)
state_data['prod_cons_ratio'] = state_data['total_production'] / state_data['consumption']

def category(ratio):
    if ratio >= 1.2:
        return 'High Producer'
    elif ratio >= 0.8:
        return 'Medium'
    else:
        return 'Low Producer'

state_data['category'] = state_data['prod_cons_ratio'].apply(category)
state_data['status'] = state_data.apply(
    lambda row: 'Exporter' if row['total_production'] > row['consumption']
    else ('Balanced' if abs(row['total_production'] - row['consumption']) < 0.05 * row['consumption']
    else 'Importer'), axis=1)

abbreviation_map = {name: abbr for abbr, name in {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire',
    'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina',
    'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania',
    'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee',
    'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington',
    'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'}.items()}
us_states['abbreviation'] = us_states['name'].map(abbreviation_map)

# === Merge GeoDataFrame
merged = us_states.merge(state_data, on='abbreviation', how='left')
merged['centroid'] = merged.geometry.centroid
merged['longitude'] = merged['centroid'].x
merged['latitude'] = merged['centroid'].y
merged = merged.drop(columns=['centroid'])

# === Map
m = folium.Map(location=[37.8, -96], zoom_start=4)

color_map = {
    'High Producer': '#1b7837',
    'Medium': '#fdae61',
    'Low Producer': '#d73027'
}

def style_function(feature):
    return {
        'fillColor': color_map.get(feature['properties']['category'], 'gray'),
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.6,
    }

def create_bar_chart(row):
    labels = ['Coal', 'Natural Gas', 'Nuclear', 'Wind', 'Solar']
    values = [row.get(e, 0) for e in labels]
    colors = ['#636363', '#3182bd', '#fd8d3c', '#31a354', '#ffd92f']
    
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(labels, values, color=colors)
    ax.set_title(f"{row['abbreviation']} Energy Production (GWh)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

# Add GeoJson with tooltip and click popups
def generate_popup_html(row):
    chart = create_bar_chart(row)
    html = f"""
    <div style="width: 400px;">
        <h4>{row['name']} ({row['abbreviation']})</h4>
        <b>Total Production:</b> {row['total_production']:.0f} GWh<br>
        <b>Consumption:</b> {row['consumption']:.0f} GWh<br>
        <b>Status:</b> {row['status']}<br>
        <b>Vulnerability Score:</b> {row['vulnerability_score']}<br><hr>
        <img src="data:image/png;base64,{chart}" width="380">
    </div>
    """
    return html

for _, row in merged.iterrows():
    popup = folium.Popup(folium.IFrame(generate_popup_html(row), width=420, height=360), max_width=450)
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=popup,
        icon=DivIcon(
            icon_size=(150, 36),
            icon_anchor=(0, 0),
            html=f'<div style="font-size:10px; color:white; text-shadow:1px 1px 2px black;">{row["abbreviation"]}</div>'
        )
    ).add_to(m)

folium.GeoJson(
    merged.to_json(),
    style_function=style_function,
    tooltip=GeoJsonTooltip(
        fields=[
            "name", "total_production", "consumption", "category", "vulnerability_score", "status",
            "Coal", "Natural Gas", "Nuclear", "Wind", "Solar"
        ],
        aliases=[
            "State:", "Total Production (GWh):", "Consumption (GWh):", "Category:", "Vulnerability Score:", "Status:",
            "Coal (GWh):", "Natural Gas (GWh):", "Nuclear (GWh):", "Wind (GWh):", "Solar (GWh):"
        ],
        localize=True,
        sticky=True,
        labels=True,
        style="background-color: white; color: black; font-size: 12px; border: 1px solid gray; padding: 5px;"
    )
).add_to(m)

# === Legend
legend_html = '''
<div style="position: fixed; top: 50px; right: 50px; width: 250px; height: 300px; 
     background-color: white; border:2px solid grey; z-index:9999; font-size:14px; padding: 20px;">
<b>Production-Consumption</b><br>
 &nbsp;<i style="background:#1b7837;color:white;padding:2px 5px;">&nbsp;</i> High Producer<br>
 &nbsp;<i style="background:#fdae61;padding:2px 5px;">&nbsp;</i> Medium<br>
 &nbsp;<i style="background:#d73027;padding:2px 5px;">&nbsp;</i> Low Producer<br>
 <hr>
<b>Vulnerability Score</b><br>
 0 → 0.5 (Low Risk)<br>
 0.5 → 1 (High Risk)<br>
 <hr>
<b>Status:</b><br>
 Exporter / Importer / Balanced
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# === Save
os.makedirs("docs", exist_ok=True)
m.save("docs/energy_production_map.html")
print("✅ Final map saved to docs/energy_production_map.html")
