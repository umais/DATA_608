from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def create_resume(output_path):
    doc = SimpleDocTemplate(output_path, pagesize=LETTER,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=30)

    styles = getSampleStyleSheet()
    story = []

    # Header
    header_style = styles['Heading1']
    header_style.fontSize = 16
    header_style.leading = 20
    story.append(Paragraph("UMAIS SIDDIQUI", header_style))
    story.append(Paragraph("Richmond, TX 77407 • 917-754-6930 • umais20@yahoo.com • https://www.linkedin.com/in/umaiss/", styles['Normal']))
    story.append(Spacer(1, 12))

    # Summary
    story.append(Paragraph("<b>Senior Backend Developer | .NET, CLOUD & MODERN WEB SOLUTIONS</b>", styles['Heading2']))
    summary = ("12+ years delivering scalable, cloud-native apps using .NET Core, Azure, Angular, React & Microservices. "
               "Proven track record leading migrations, modernizations, and CQRS-based architectures in Agile environments. "
               "Passionate about automation, DevOps, and building resilient systems.")
    story.append(Paragraph(summary, styles['Normal']))
    story.append(Spacer(1, 12))

    # Technical Skills Table
    story.append(Paragraph("<b>TECHNICAL SKILLS</b>", styles['Heading2']))

    skills_data = [
        ["Languages:", "C#, Python, T-SQL, JavaScript, TypeScript"],
        ["Frameworks:", ".NET Core/5/6/8, ASP.NET MVC/Web API, Flask, Django Angular, React, Node.js"],
        ["Cloud & DevOps:", "Azure (App Services, Functions, AKS), AWS Lambda, Docker, Kubernetes, Azure DevOps, GitHub Actions"],
        ["Databases:", "SQL Server, Elasticsearch, MongoDB, DynamoDB"],
        ["Tools:", "JIRA, Confluence, ServiceNow, RabbitMQ, Redis"]
    ]

    table = Table(skills_data, colWidths=[100, 360])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(table)
    story.append(Spacer(1, 12))

    # Experience
    story.append(Paragraph("<b>PROFESSIONAL EXPERIENCE</b>", styles['Heading2']))

    experience_entries = [
        ("Harris County Universal Services — Technical Lead", "July 2023 – Present", [
            "Led migration from .NET Framework to .NET 8 microservices and Azure, improving scalability and performance.",
            "Modernized LENS UI using .NET Core, Angular, and containerization on AKS.",
            "Implemented CQRS architecture and RabbitMQ pub/sub for real-time data ingestion.",
            "Enhanced DevOps pipelines (CI/CD) using Azure DevOps and GitHub Actions."
        ]),
        ("Burnett Specialists — Senior Software Engineer (Consultant)", "July 2022 – July 2023", [
            "Refactored monoliths to microservices using .NET 6,Python flask, Docker, and Kubernetes.",
            "Modernized apps with React & Minimal APIs, improving load times by 30%.",
            "Applied SOLID and design patterns for maintainable, testable codebases.",
            "Integrated monitoring and performance tools for proactive issue detection.",
            "Implemented CI/CD pipelines using GitHub Actions to On-Premisis and AWS Cloud environments."
        ]),
        ("Rural Sourcing — Senior Software Engineer", "March 2022 – Feb 2023", [
            "Built scalable SPAs with Angular and React, backed by .NET Core microservices.",
            "Designed CQRS microservices and optimized Elasticsearch queries for large datasets.",
            "Directed CI/CD pipelines across AWS & Azure environments."
        ]),
        ("Previous Experience", "2007 – 2022", [
            ".NET Developer III — Alvarez & Marsal (2019–2022)",
            "Manager Software Eng — AlignCare (2015–2019)",
            "Digital Asset Manager — HarperCollins (2013–2015)",
            "Lead Product Designer — TriZetto (2010–2013)",
            "Software Developer — AlignCare (2007–2010)"
        ])
    ]

    for title, date, bullets in experience_entries:
        story.append(Paragraph(f"<b>{title}</b> <font size=9>({date})</font>", styles['Normal']))
        for bullet in bullets:
            story.append(Paragraph(f"• {bullet}", styles['Normal']))
        story.append(Spacer(1, 6))

    # Education
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>EDUCATION</b>", styles['Heading2']))
    story.append(Paragraph("Master's in Data Science (In Progress), CUNY SPS, NY", styles['Normal']))
    story.append(Paragraph("Bachelor of Computer Science, Queens College (CUNY), 2017", styles['Normal']))

    doc.build(story)


# Usage
create_resume("umais_siddiqui_resume.pdf")
