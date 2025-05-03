from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import textwrap

# Define the scenario/use case
use_case = {
    "title": "Student Survey: Study Habits During Finals",
    "introduction": "Understanding how students prepare for final exams can help improve support programs. Here's a snapshot of study habits based on our latest survey.",
    "key_points": [
        "72% of students prefer studying at night.",
        "58% use online study resources.",
        "Only 25% attend review sessions regularly.",
        "Top challenges: time management (45%), stress (35%)"
    ],
    "flow": ["Survey Purpose", "Study Preferences", "Resource Usage", "Challenges Faced"]
}

# Create a pie chart for study preferences
study_methods = ['Night Study', 'Day Study', 'Both']
percentages = [72, 20, 8]

plt.figure(figsize=(5,5))
plt.pie(percentages, labels=study_methods, autopct='%1.1f%%', startangle=140,
        colors=["#66b3ff", "#99ff99", "#ffcc99"])
plt.title('When Students Prefer to Study')
plt.savefig('study_pie_chart.png', bbox_inches='tight')
plt.close()

# Load fonts
try:
    font_title = ImageFont.truetype("arialbd.ttf", 40)
    font_subtitle = ImageFont.truetype("arial.ttf", 24)
    font_text = ImageFont.truetype("arial.ttf", 20)
except:
    font_title = ImageFont.load_default()
    font_subtitle = ImageFont.load_default()
    font_text = ImageFont.load_default()

# Helper function for wrapping text
def draw_wrapped_text(draw, text, position, font, max_width, line_spacing=5):
    lines = textwrap.wrap(text, width=60)
    x, y = position
    for line in lines:
        draw.text((x, y), line, fill="black", font=font)
        bbox = font.getbbox(line)  # (x0, y0, x1, y1)
        line_height = bbox[3] - bbox[1]
        y += line_height + line_spacing
    return y

# Create infographic canvas
width, height = 800, 1500
infographic = Image.new('RGB', (width, height), color='white')
draw = ImageDraw.Draw(infographic)

# Title
draw.text((50, 30), use_case["title"], fill="black", font=font_title)

# Introduction (wrapped)
y_pos = draw_wrapped_text(draw, use_case["introduction"], (50, 100), font_subtitle, 700)

# Insert pie chart
chart = Image.open('study_pie_chart.png').resize((400, 400))
infographic.paste(chart, (200, y_pos + 20))
y_pos += 440

# Key findings
draw.text((50, y_pos), "Key Findings:", fill="black", font=font_subtitle)
y_pos += 40
for point in use_case["key_points"]:
    y_pos = draw_wrapped_text(draw, f"- {point}", (70, y_pos), font_text, 660)

# Flow section
y_pos += 30
draw.text((50, y_pos), "Flow:", fill="black", font=font_subtitle)
y_pos += 40
for step in use_case["flow"]:
    draw.text((70, y_pos), f"> {step}", fill="black", font=font_text)
    y_pos += 30

# Save infographic
infographic.save('final_infographic.png')
print("Infographic created successfully: 'final_infographic.png'")
