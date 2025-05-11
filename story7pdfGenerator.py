from fpdf import FPDF
import os

# === User Details ===
your_name = "Umais Siddiqui"
your_class = "DATA 608"
story_title = "Story 7: U.S. Energy Production Analysis"
map_image = "energyMap.png"
hosted_map_url = "https://umais.github.io/DATA_608/energy_production_map.html"  # Replace with your actual URL

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
# === PAGE 2: Map Screenshot ===
pdf.add_page()
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "Interactive Map Screenshot", ln=True, align="C")
pdf.ln(10)

# Check if image exists
if os.path.exists(map_image):
   pdf.image(map_image, x=10, w=190)

else:
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Error: {map_image} not found in directory.", ln=True, align="C")

# Add the link below the image
pdf.ln(10)
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "View the interactive map here:", ln=True, align="C")
pdf.set_text_color(0, 0, 255)  # Blue link
pdf.cell(0, 10, hosted_map_url, ln=True, align="C", link=hosted_map_url)
pdf.set_text_color(0, 0, 0)  # Reset back to black


# === PAGE 3: Insights + URL ===
pdf.add_page()
pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "Insights & Observations", ln=True, align="L")
pdf.ln(10)

pdf.set_font("Arial", "", 12)
paragraph1 = (
    "The U.S. energy production map reveals distinct regional patterns that highlight the nation's energy landscape. "
    "The central and western states, particularly Texas, Wyoming, and North Dakota, emerge as high energy producers "
    "(shown in blue), functioning as net exporters with robust production capabilities across multiple energy sources. "
    "Texas stands out with its massive production of 25.3 trillion GWh, primarily from natural gas and wind. "
    "In contrast, coastal states including California, New York, and most of New England (shown in red) demonstrate "
    "lower production levels relative to their consumption, making them dependent on energy imports from other regions."
)

paragraph2 = (
    "The energy mix varies significantly by region, reflecting each area's natural resources and policy priorities. "
    "Coal remains dominant in Wyoming and West Virginia, while natural gas leads in Texas and Pennsylvania. "
    "Nuclear energy provides significant baseload power in states like Illinois and Pennsylvania, while wind energy "
    "has gained prominence in the Great Plains states. The vulnerability scores indicate each state's exposure to "
    "potential energy disruptions, with higher scores (closer to 1.0) suggesting greater dependency on external sources "
    "and less diversified energy portfolios."
)

vulnerability_paragraph = (
    "The vulnerability score (ranging from 0.0 to 1.0) serves as a critical indicator of energy security, with lower "
    "values representing stronger resilience. States like Texas and Wyoming show minimal vulnerability (scores near 0), "
    "indicating self-sufficiency and export capacity. Meanwhile, states with higher scores face greater exposure to "
    "supply disruptions, price volatility, and transmission constraints. These regional disparities highlight the need "
    "for robust interstate transmission infrastructure and strategic energy policy to enhance national energy security "
    "while supporting the ongoing transition to cleaner energy sources."
)

data_source = (
    "Data Source: U.S. Energy Information Administration (EIA) State Energy Data System (SEDS), "
    "which provides comprehensive state energy statistics. The data includes production and consumption "
    "figures for all energy sources, allowing for detailed analysis of energy flows and dependencies "
    "between states. More information available at: https://www.eia.gov/state/seds/"
)

pdf.multi_cell(0, 10, paragraph1)
pdf.ln(5)
pdf.multi_cell(0, 10, paragraph2)
pdf.ln(5)
pdf.multi_cell(0, 10, vulnerability_paragraph)
pdf.ln(10)
pdf.set_font("Arial", "I", 10)  # Italics for data source
pdf.multi_cell(0, 10, data_source)
pdf.ln(10)
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "View the interactive map here:", ln=True)
pdf.set_text_color(0, 0, 255)  # Blue link
pdf.cell(0, 10, hosted_map_url, ln=True, link=hosted_map_url)

# === SAVE PDF ===
output_pdf = "energy_production_report.pdf"
pdf.output(output_pdf)
print(f"✅ PDF report saved as {output_pdf}")
