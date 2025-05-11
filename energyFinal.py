import os
import pandas as pd
import geopandas as gpd
import folium
from folium.features import DivIcon, GeoJsonTooltip, Popup
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import matplotlib.patheffects as path_effects
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

# Map MSN codes to energy types
msn_to_type = {
    'CLPRB': 'Coal', 'CLPRK': 'Coal', 'CLPRP': 'Coal',
    'NGMPB': 'Natural Gas', 'NGMPK': 'Natural Gas', 'NGMPP': 'Natural Gas',
    'NUEGP': 'Nuclear', 'NUETB': 'Nuclear',
    'WYTCB': 'Wind'
}
energy_df['Energy_Type'] = energy_df['MSN'].map(msn_to_type)
energy_df = energy_df[energy_df['Energy_Type'].notna()]
energy_df['abbreviation'] = energy_df['State'].str.strip().str.upper()
energy_df['2022'] = energy_df['2022'].astype(str).str.replace(',', '', regex=False).astype(float)

# Aggregate production breakdown
energy_breakdown = energy_df.groupby(['abbreviation', 'Energy_Type']).agg({'2022': 'sum'}).reset_index()
energy_pivot = energy_breakdown.pivot(index='abbreviation', columns='Energy_Type', values='2022').reset_index().fillna(0)
energy_pivot['total_production'] = energy_pivot[['Coal', 'Natural Gas', 'Nuclear', 'Wind']].sum(axis=1)

# === Merge with consumption
state_data = pd.merge(consumption_2022, energy_pivot, on='abbreviation', how='left')
state_data['vulnerability_score'] = round(
    (state_data['consumption'] - state_data['total_production']) / state_data['consumption'], 2
)
state_data['vulnerability_score'] = state_data['vulnerability_score'].clip(lower=0).fillna(0)

# Define High/Medium/Low category
state_data['prod_cons_ratio'] = state_data['total_production'] / state_data['consumption']
def category(ratio):
    if ratio >= 1.2:
        return 'High Producer'
    elif ratio >= 0.8:
        return 'Medium'
    else:
        return 'Low Producer'
state_data['category'] = state_data['prod_cons_ratio'].apply(category)

# === Map full state names to abbreviations
abbreviation_map = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA', 'Colorado': 'CO',
    'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
    'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
    'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}
us_states['abbreviation'] = us_states['name'].map(abbreviation_map)

# === Merge GeoDataFrame
merged = us_states.merge(state_data, on='abbreviation', how='left')

merged['centroid'] = merged.geometry.centroid
merged['longitude'] = merged['centroid'].x
merged['latitude'] = merged['centroid'].y
merged = merged.drop(columns=['centroid'])

# === INTERACTIVE MAP ===
m = folium.Map(location=[37.8, -96], zoom_start=4)

# Define color function for categories
def color_function(feature):
    category = feature['properties']['category']
    if category == 'High Producer':
        return '#006d2c'  # dark green
    elif category == 'Medium':
        return '#fd8d3c'  # orange
    elif category == 'Low Producer':
        return '#a50f15'  # dark red
    else:
        return 'gray'

# Add states GeoJson
folium.GeoJson(
    merged.to_json(),
    style_function=lambda feature: {
        'fillColor': color_function(feature),
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.6,
    },
    tooltip=GeoJsonTooltip(
        fields=[
            "name", "total_production", "consumption", "category", "vulnerability_score",
            "Coal", "Natural Gas", "Nuclear", "Wind"
        ],
        aliases=[
            "State:", "Total Production (GWh):", "Consumption (GWh):", "Category:", "Vulnerability Score:",
            "Coal (GWh):", "Natural Gas (GWh):", "Nuclear (GWh):", "Wind (GWh):"
        ],
        localize=True,
        sticky=True,
        labels=True,
        style="background-color: white; color: black; font-size: 12px; border: 1px solid gray; padding: 5px;"
    )
).add_to(m)

# === Pie Chart per state popup ===
os.makedirs("docs/pies", exist_ok=True)

for _, row in merged.iterrows():
    if row['total_production'] > 0:
        labels = ['Coal', 'Natural Gas', 'Nuclear', 'Wind']
        sizes = [row.get('Coal', 0), row.get('Natural Gas', 0), row.get('Nuclear', 0), row.get('Wind', 0)]
        colors_pie = ['#636363', '#3182bd', '#fd8d3c', '#31a354']
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')
        plt.title(f"{row['abbreviation']} Production Breakdown")

        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')

        html = f'<img src="data:image/png;base64,{img_base64}" width="250" height="250">'
        iframe = folium.IFrame(html, width=270, height=270)
        popup = Popup(iframe, max_width=270)

        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup,
            icon=DivIcon(
                icon_size=(150, 36),
                icon_anchor=(0, 0),
                html=f'<div style="font-size:10px; color:white; text-shadow:1px 1px 2px black;">{row["abbreviation"]}</div>'
            )
        ).add_to(m)

# === Add Legend (Moved to Top-Right Corner) ===
# === Add Larger Legend (Moved to Top-Right Corner) ===
legend_html = '''
<div style="position: fixed; 
     top: 50px; right: 50px; width: 250px; height: 250px; 
     background-color: white; border:2px solid grey; z-index:9999; font-size:14px; padding: 20px;">
<b>Production-Consumption</b><br>
 &nbsp;<i style="background:#006d2c;color:white;padding:2px 5px;">&nbsp;</i> High Producer<br>
 &nbsp;<i style="background:#fd8d3c;padding:2px 5px;">&nbsp;</i> Medium<br>
 &nbsp;<i style="background:#a50f15;padding:2px 5px;">&nbsp;</i> Low Producer<br>
 <hr>
<b>Vulnerability Score</b><br>
 0 → 0.5 (Low Risk)<br>
 0.5 → 1 (High Risk)
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))


# Save interactive map
os.makedirs("docs", exist_ok=True)
m.save("docs/energy_production_map.html")
print("✅ Enhanced map with legend saved to docs/energy_production_map.html")
