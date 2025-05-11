import os
import pandas as pd
import geopandas as gpd
import folium
from folium.features import DivIcon, GeoJsonTooltip
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import matplotlib.patheffects as path_effects
from shapely.geometry import Point

# === Load US States GeoJSON ===
us_states = gpd.read_file("https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json")

# === Dummy Energy Production Data ===
state_energy = pd.DataFrame({
    'name': us_states['name'],
    'coal': range(0, len(us_states) * 100, 100),
    'solar': range(0, len(us_states) * 20, 20),
    'wind': range(0, len(us_states) * 50, 50),
    'hydro': range(0, len(us_states) * 30, 30)
})
state_energy['total'] = state_energy[['coal', 'solar', 'wind', 'hydro']].sum(axis=1)

# === Add Additional Relevant Data Points ===
state_energy['import_export_status'] = ['Net Exporter' if i % 2 == 0 else 'Net Importer' for i in range(len(state_energy))]
state_energy['vulnerability_score'] = [round(0.1 * (i % 10), 2) for i in range(len(state_energy))]

# === Merge GeoDataFrame with Energy Data ===
merged = us_states.merge(state_energy, on='name')

# === Calculate Centroids for Labeling ===
merged['centroid'] = merged.geometry.centroid
merged['longitude'] = merged['centroid'].x
merged['latitude'] = merged['centroid'].y

# Remove the centroid column before passing to GeoJSON serialization
merged = merged.drop(columns=['centroid'])

# === INTERACTIVE MAP ===
m = folium.Map(location=[37.8, -96], zoom_start=4)

choropleth = folium.Choropleth(
    geo_data=merged.to_json(),
    name="Energy Production",
    data=merged,
    columns=["name", "total"],
    key_on="feature.properties.name",
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Total Energy Production (GWh)",
    highlight=True,
).add_to(m)

# === Updated Tooltip with Extra Fields ===
tooltip = GeoJsonTooltip(
    fields=["name", "coal", "solar", "wind", "hydro", "total", "import_export_status", "vulnerability_score"],
    aliases=["State:", "Coal:", "Solar:", "Wind:", "Hydro:", "Total:", "Import/Export Status:", "Vulnerability Score:"],
    localize=True,
    sticky=True,
    labels=True,
    style="background-color: white; color: black; font-size: 12px; border: 1px solid gray; padding: 5px;"
)

choropleth.geojson.add_child(tooltip)

# Add text labels
for _, row in merged.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        icon=DivIcon(
            icon_size=(150, 36),
            icon_anchor=(0, 0),
            html=f'<div style="font-size:10px; color:white; text-shadow:1px 1px 2px black;">{row["name"]}</div>'
        )
    ).add_to(m)

# Save interactive map
os.makedirs("docs", exist_ok=True)
m.save("docs/energy_production_map.html")
print("✅ Interactive map saved to docs/energy_production_map.html")

# === STATIC MAP (PDF) ===
# Plot using original CRS (EPSG:4326)
norm = Normalize(vmin=merged['total'].min(), vmax=merged['total'].max())
cmap = cm.get_cmap("viridis")
colors = [cmap(norm(val)) for val in merged["total"]]

fig, ax = plt.subplots(1, 1, figsize=(14, 10))
merged.plot(ax=ax, color=colors, edgecolor="black", alpha=0.7)

# Annotate state names
for _, row in merged.iterrows():
    txt = ax.text(
        row['longitude'], row['latitude'], row['name'],
        fontsize=6, ha='center', va='center', color='white'
    )
    txt.set_path_effects([path_effects.withStroke(linewidth=1.5, foreground="black")])

# Add colorbar
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm._A = []
cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.04)
cbar.set_label('Total Energy Production (GWh)', fontsize=12)

plt.title("U.S. Statewise Energy Production Breakdown", fontsize=16, fontweight="bold")
ax.axis("off")

# Save static map
plt.savefig("docs/energy_production_map.pdf", dpi=300, bbox_inches='tight')
plt.close()
print("✅ Static map saved to docs/energy_production_map.pdf")
