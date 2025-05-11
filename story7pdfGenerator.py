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
    "The U.S. energy production map shows clear regional distinctions. States in the central and western U.S., "
    "such as Texas, Oklahoma, and Wyoming, stand out as high energy producers, marked in green. "
    "These states not only generate significant amounts of energy but also act as net exporters. "
    "In contrast, states along the East and West Coasts, including California, New York, and most of New England, "
    "are marked as low producers and are likely dependent on imported energy, indicated by the red shading."
)

paragraph2 = (
    "Hydropower appears to be significant in the Pacific Northwest (e.g., Washington), while natural gas and wind "
    "dominate in high-production states like Texas. The map also categorizes states by their vulnerability scores, "
    "with lower scores reflecting stronger energy resilience. Texas, for example, shows a vulnerability score of 0, "
    "suggesting a diverse and robust energy profile with minimal supply risk."
)

vulnerability_paragraph = (
    "The vulnerability score ranges from 0.0 to 1.0, where lower values indicate stronger energy resilience. "
    "A score of 0.0, as seen in Texas, represents a state with highly diversified energy sources and minimal dependency "
    "on imports. In contrast, states shaded in red with higher scores may face challenges such as reliance on a single "
    "energy type or exposure to supply disruptions. Monitoring and addressing these vulnerabilities is essential "
    "for national energy security."
)

pdf.multi_cell(0, 10, paragraph1)
pdf.ln(5)
pdf.multi_cell(0, 10, paragraph2)
pdf.ln(5)
pdf.multi_cell(0, 10, vulnerability_paragraph)
pdf.ln(10)
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "View the interactive map here:", ln=True)
pdf.set_text_color(0, 0, 255)  # Blue link
pdf.cell(0, 10, hosted_map_url, ln=True, link=hosted_map_url)

# === SAVE PDF ===
output_pdf = "energy_production_report.pdf"
pdf.output(output_pdf)
print(f"✅ PDF report saved as {output_pdf}")
