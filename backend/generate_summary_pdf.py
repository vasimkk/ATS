import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

def generate_pdf():
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Project_Summary.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=50,
        rightMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title',
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor("#1e1b4b"),
        spaceAfter=10
    )
    
    h1_style = ParagraphStyle(
        'H1',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor("#4338ca"),
        spaceBefore=15,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'Body',
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#334155"),
        spaceAfter=10
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#334155"),
        leftIndent=20,
        spaceAfter=6
    )

    story = []
    
    # Title
    story.append(Paragraph("ResuMatch ATS Studio", title_style))
    story.append(Paragraph("Project Update Summary & Logical Flow", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4338ca"), spaceAfter=15))
    
    # Section 1
    story.append(Paragraph("Project Description", h1_style))
    story.append(Paragraph(
        "ResuMatch ATS Studio is an intelligent recruitment engineering platform designed to score candidate resumes against target job descriptions. In our recent updates, we fundamentally transformed the system's core matching logic from a strict keyword-counting system into a state-of-the-art AI semantic engine.",
        body_style
    ))
    
    story.append(Spacer(1, 10))
    
    # Section 2
    story.append(Paragraph("Logical Flow & Architectural Changes", h1_style))
    
    story.append(Paragraph("<b>1. Transition to 100% Vector Semantic Scoring</b>", body_style))
    story.append(Paragraph(
        "The previous multi-factor scoring algorithm (which weighed exact keyword matches, structural readability, and experience) was completely stripped away. The system now scores a resume entirely based on meaning, evaluating how well the candidate's achievements semantically resonate with the job requirements.",
        bullet_style
    ))
    
    story.append(Paragraph("<b>2. Integration of HuggingFace LLM (all-MiniLM-L6-v2)</b>", body_style))
    story.append(Paragraph(
        "The legacy local TF-IDF model was replaced with a pre-trained neural network. This allows the system to instantly recognize that terms like 'React' and 'Frontend' are highly related, preventing candidates from being penalized for missing exact keywords.",
        bullet_style
    ))
    
    story.append(Paragraph("<b>3. Dimensionality Scaling (384-D Space)</b>", body_style))
    story.append(Paragraph(
        "By utilizing the new HuggingFace model, the mathematical vector space was expanded from 128 to 384 dimensions, providing an exponentially deeper understanding of context and nuance.",
        bullet_style
    ))
    
    story.append(Paragraph("<b>4. Frontend UI Optimization</b>", body_style))
    story.append(Paragraph(
        "The React application was simplified to remove contradictions. We deleted the 'Keyword Gap Matrix' and unnecessary non-vector breakdown cards to ensure the user interface accurately reflects the new semantic-only scoring philosophy.",
        bullet_style
    ))
    
    story.append(Paragraph("<b>5. Customized Job Taxonomy</b>", body_style))
    story.append(Paragraph(
        "Custom, highly-targeted job profiles (e.g., 'Java Full Stack Developer' and 'Frontend Lead') were injected into the database to accurately validate and test specific candidate profiles against the new engine.",
        bullet_style
    ))
    
    doc.build(story)
    print(f"PDF successfully generated at: {pdf_path}")

if __name__ == "__main__":
    generate_pdf()
