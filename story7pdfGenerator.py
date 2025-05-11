from fpdf import FPDF
import os

# === User Details ===
your_name = "Umais Siddiqui"
your_class = "DATA 608"
story_title = "Story 7: U.S. Energy Production Analysis"
map_image = "energyMap.png"
hosted_map_url = "https://yourusername.github.io/energy_production_map.html"  # Replace with your actual URL

# === Create PDF ===
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)

# === PAGE 1: Cover Page ===
pdf.add_page()
pdf.set_font("Arial", "B", 24)
pdf.cell(0, 60, "", ln=True)  # Spacer
pdf.cell(0, 10, story_title, ln=True, align="C")
pdf.ln(20)
pdf.set_font("Arial", "", 18)
pdf.cell(0, 10, f"Name: {your_name}", ln=True, align="C")
pdf.cell(0, 10, f"Class: {your_class}", ln=True, align="C")

# === PAGE 2: Map Screenshot ===
pdf.add_page()
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "Interactive Map Screenshot", ln=True, align="C")
pdf.ln(10)

# Check if image exists
if os.path.exists(map_image):
    pdf.image(map_image, x=20, w=170)
else:
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Error: {map_image} not found in directory.", ln=True, align="C")

# === PAGE 3: Insights + URL ===
pdf.add_page()
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "Insights & Observations", ln=True, align="L")
pdf.ln(10)

pdf.set_font("Arial", "", 12)
paragraph1 = ("The interactive energy production map reveals distinct regional patterns in the U.S. "
              "States in the Midwest and Great Plains tend to be strong producers of wind energy, while "
              "hydropower is concentrated in the Pacific Northwest. The map also highlights which states "
              "are net energy exporters versus importers, providing insights into regional energy independence.")

paragraph2 = ("Furthermore, the vulnerability score overlay helps identify states that may face challenges "
              "in energy resilience. States with higher vulnerability scores may need to diversify their "
              "energy sources or improve infrastructure. The interactive map allows for a deeper exploration "
              "of these patterns and trends.")

pdf.multi_cell(0, 10, paragraph1)
pdf.ln(5)
pdf.multi_cell(0, 10, paragraph2)
pdf.ln(10)

pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "View the interactive map here:", ln=True)
pdf.set_text_color(0, 0, 255)  # Blue link
pdf.cell(0, 10, hosted_map_url, ln=True, link=hosted_map_url)

# === SAVE PDF ===
output_pdf = "energy_production_report.pdf"
pdf.output(output_pdf)
print(f"✅ PDF report saved as {output_pdf}")
