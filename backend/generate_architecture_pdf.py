"""
Architecture and System Specifications PDF Generator for ResuMatch ATS Studio.
Uses ReportLab to generate a publication-quality technical PDF document.
"""
import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and display total page numbers."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (pages after page 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "ResuMatch ATS Studio — Architectural Specifications & System Design")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 742, letter[0] - 54, 742)

        # Footer
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 45, letter[0] - 54, 45)
        
        self.drawString(54, 32, "Confidential — Engineering Documentation")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(letter[0] - 54, 32, page_str)
        self.restoreState()

def build_pdf(filename="ResuMatch_ATS_Project_Architecture.pdf"):
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#1e1b4b")
    indigo = colors.HexColor("#4338ca")
    slate = colors.HexColor("#334155")
    card_bg = colors.HexColor("#f8fafc")
    border_color = colors.HexColor("#e2e8f0")

    doc_title_style = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=6
    )
    doc_subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=indigo,
        spaceAfter=14
    )
    h1_style = ParagraphStyle(
        'Header1',
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Header2',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=indigo,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyDark',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=slate,
        spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        'BulletText',
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=slate,
        leftIndent=12,
        spaceAfter=3
    )
    callout_style = ParagraphStyle(
        'CalloutText',
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b")
    )
    table_cell_style = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=slate
    )
    table_header_style = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.white
    )

    story = []

    # 1. Document Title & Header
    story.append(Paragraph("ResuMatch ATS Studio", doc_title_style))
    story.append(Paragraph("System Architecture, Vector Embeddings & Technical Specifications", doc_subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=indigo, spaceBefore=2, spaceAfter=12))

    # Meta Information Box
    meta_data = [
        [
            Paragraph("<b>Stack:</b> Python 3.14 (FastAPI) + React JS (Vite)", table_cell_style),
            Paragraph("<b>Version:</b> 1.2.0 (Production Architecture)", table_cell_style)
        ],
        [
            Paragraph("<b>Vector Dimension:</b> 128-D Dense Latent Semantic Embeddings", table_cell_style),
            Paragraph("<b>Document Scope:</b> End-to-End System Specifications", table_cell_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[270, 234])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 2. Project Purpose & Executive Summary
    story.append(Paragraph("1. Executive Summary & Project Purpose", h1_style))
    story.append(Paragraph(
        "<b>ResuMatch ATS Studio</b> is an intelligent, full-stack recruitment engineering platform designed to bridge "
        "the gap between job candidates and modern Applicant Tracking Systems (ATS) like Workday, Taleo, Greenhouse, and Lever. "
        "Modern ATS platforms utilize multi-stage screening filters combining keyword taxonomies, TF-IDF lexical frequency, "
        "formatting compliance, and high-dimensional semantic vector embeddings to rank candidates.",
        body_style
    ))
    story.append(Paragraph(
        "The application accepts candidate resumes via <b>direct file upload (PDF, DOCX, TXT)</b> with no manual typing needed, "
        "ingests target job descriptions, computes an empirical <b>ATS Match Score (0–100%)</b> with point-by-point vector resonance, "
        "and automatically synthesizes an updated, tailored resume featuring STAR-method (Situation, Task, Action, Result) achievements "
        "and downloadable Microsoft Word (.docx) export.",
        body_style
    ))

    # 3. High-Level Architecture
    story.append(Paragraph("2. High-Level System Architecture", h1_style))
    story.append(Paragraph(
        "The system follows a modular, decoupled client-server architecture. The backend is built with <b>Python 3.14 and FastAPI</b> "
        "providing high-performance asynchronous REST endpoints, while the frontend is built with <b>React JS and Vite</b> "
        "utilizing a modern dark glassmorphic design system.",
        body_style
    ))

    arch_data = [
        [Paragraph("Module", table_header_style), Paragraph("Technology / Libraries", table_header_style), Paragraph("Key Functional Responsibilities", table_header_style)],
        [
            Paragraph("<b>Frontend SPA</b>", table_cell_style),
            Paragraph("React 18, Vite, Vanilla CSS, Lucide Icons", table_cell_style),
            Paragraph("Upload-only file dropzone, radial SVG score gauge, interactive Keyword Gap Matrix, Vector Resonance table, and side-by-side diff viewer.", table_cell_style)
        ],
        [
            Paragraph("<b>API Gateway</b>", table_cell_style),
            Paragraph("FastAPI, Uvicorn, CORS, StreamingResponse", table_cell_style),
            Paragraph("Asynchronous request orchestration, multipart file ingestion, validation, and docx binary streaming.", table_cell_style)
        ],
        [
            Paragraph("<b>Document Parser</b>", table_cell_style),
            Paragraph("pypdf, python-docx, Regex", table_cell_style),
            Paragraph("Text extraction from binary PDF/DOCX, section segmentation (Experience, Education, Skills), contact metadata extraction.", table_cell_style)
        ],
        [
            Paragraph("<b>Vector Engine</b>", table_cell_style),
            Paragraph("Scikit-Learn, TruncatedSVD, Cosine Similarity", table_cell_style),
            Paragraph("128-D dense vector embeddings generation, overall vector cosine distance, point-by-point requirement matching.", table_cell_style)
        ],
        [
            Paragraph("<b>ATS Scoring Engine</b>", table_cell_style),
            Paragraph("Multi-factor weighted algorithm, TF-IDF", table_cell_style),
            Paragraph("Multi-factor scoring (Hard Skills, Vector, TF-IDF, Readability, Soft Skills, Experience), letter grade assignment.", table_cell_style)
        ],
        [
            Paragraph("<b>Resume Optimizer</b>", table_cell_style),
            Paragraph("NLP rewrite rules, STAR templates", table_cell_style),
            Paragraph("Dynamic tailored summary generation, STAR-method bullet rewriting with injected missing keywords, zero static data.", table_cell_style)
        ],
        [
            Paragraph("<b>Document Exporter</b>", table_cell_style),
            Paragraph("python-docx, XML Open Packaging", table_cell_style),
            Paragraph("Generates ATS-standard Microsoft Word documents with compliant typography, margins, and native bullet structures.", table_cell_style)
        ],
    ]
    arch_table = Table(arch_data, colWidths=[100, 150, 254])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), indigo),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, card_bg]),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 10))

    # 4. Vector Embeddings Deep Dive
    story.append(Paragraph("3. Vector Embeddings & Semantic Vectorization Engine", h1_style))
    story.append(Paragraph(
        "Modern recruiting platforms employ dense vector embeddings to measure contextual proximity rather than purely relying on exact string matches. "
        "The <b>VectorEmbeddingEngine</b> (implemented in <code>vector_engine.py</code>) provides continuous 128-dimensional dense vector embeddings:",
        body_style
    ))
    story.append(Paragraph("• <b>Dual-Ngram Latent Semantic Projection:</b> Ingests text and builds unigram and bigram term distributions with sublinear term-frequency scaling to prevent outlier token domination.", bullet_style))
    story.append(Paragraph("• <b>Dimensionality Reduction (TruncatedSVD):</b> Reduces the high-dimensional sparse token matrix into a compact 128-dimensional dense continuous latent semantic space (preserving over 90% of semantic variance).", bullet_style))
    story.append(Paragraph("• <b>L2 Vector Normalization:</b> Normalizes vectors to unit length so that Cosine Similarity equals the inner dot product: <i>cos(θ) = (u · v) / (||u|| ||v||)</i>.", bullet_style))
    story.append(Paragraph("• <b>Point-by-Point Requirement Resonance:</b> The engine splits the job description into discrete responsibility and qualification statements, vectorizes each item individually, and matches it against each bullet vector in the candidate's resume.", bullet_style))
    story.append(Paragraph("• <b>Coverage Metrics:</b> Produces a coverage percentage showing what proportion of JD requirement vectors have a high resonance (>=72%) or moderate resonance (52–71%) in the candidate's resume.", bullet_style))

    story.append(Spacer(1, 6))

    # 5. ATS Scoring Algorithm
    story.append(Paragraph("4. Multi-Factor ATS Compatibility Scoring Algorithm", h1_style))
    story.append(Paragraph(
        "To simulate real enterprise ATS scanners, the platform does not rely on a single metric. Instead, it computes an empirical weighted composite score:",
        body_style
    ))

    score_data = [
        [Paragraph("Scoring Dimension", table_header_style), Paragraph("Weight", table_header_style), Paragraph("Evaluation Methodology & Logic", table_header_style)],
        [
            Paragraph("<b>Hard Technical Skills</b>", table_cell_style),
            Paragraph("<b>30%</b>", table_cell_style),
            Paragraph("Exact and synonym matching against 1,000+ categorized skills (languages, frameworks, databases, cloud, DevOps, AI/ML tools).", table_cell_style)
        ],
        [
            Paragraph("<b>Dense Vector Embeddings</b>", table_cell_style),
            Paragraph("<b>20%</b>", table_cell_style),
            Paragraph("128-D dense vector cosine similarity measuring overall contextual resonance and semantic alignment between candidate profile and JD.", table_cell_style)
        ],
        [
            Paragraph("<b>TF-IDF Lexical Similarity</b>", table_cell_style),
            Paragraph("<b>15%</b>", table_cell_style),
            Paragraph("Evaluates broader vocabulary overlap, domain terminology density, and technical jargon consistency.", table_cell_style)
        ],
        [
            Paragraph("<b>ATS Structural Readability</b>", table_cell_style),
            Paragraph("<b>15%</b>", table_cell_style),
            Paragraph("Structural scan: contact info (email, phone, LinkedIn), standard section headers (Experience, Skills, Education), bullet point density (>=5), optimal word count (400-1000).", table_cell_style)
        ],
        [
            Paragraph("<b>Soft Skills & Leadership</b>", table_cell_style),
            Paragraph("<b>10%</b>", table_cell_style),
            Paragraph("Presence of essential execution keywords: cross-functional collaboration, mentorship, agile delivery, problem-solving, stakeholder management.", table_cell_style)
        ],
        [
            Paragraph("<b>Experience & Seniority</b>", table_cell_style),
            Paragraph("<b>10%</b>", table_cell_style),
            Paragraph("Detection of years of experience stated in candidate resume versus years required by JD (e.g. 4+ years), plus degree matching.", table_cell_style)
        ],
    ]
    score_table = Table(score_data, colWidths=[120, 50, 334])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, card_bg]),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 10))

    # 6. Resume Optimization & Tailoring Pipeline
    story.append(Paragraph("5. Dynamic Resume Tailoring & Optimization Pipeline", h1_style))
    story.append(Paragraph(
        "When the user clicks <b>'Update Resume for JD'</b>, the system invokes <code>optimize_resume()</code> in <code>resume_optimizer.py</code>. "
        "The tailoring pipeline operates with <b>Zero Static Fake Data</b>, adhering strictly to candidate authenticity:",
        body_style
    ))
    story.append(Paragraph("1. <b>Keyword Gap Extraction:</b> Identifies skills present in the target job description that are missing from the candidate's resume.", bullet_style))
    story.append(Paragraph("2. <b>Dynamic Summary Synthesis:</b> Crafts a targeted Professional Summary mentioning the exact target role and candidate's actual extracted years of experience (without hardcoding fake numbers).", bullet_style))
    story.append(Paragraph("3. <b>STAR Bullet Point Optimization:</b> Upgrades existing work experience bullet points using the <b>Situation, Task, Action, Result</b> framework, naturally weaving in missing technical tools and quantified impact metrics.", bullet_style))
    story.append(Paragraph("4. <b>Skills Matrix Restructuring:</b> Organizes skills into standard ATS categories (Programming Languages, Frameworks, Cloud & DevOps, Databases) with missing competencies injected.", bullet_style))
    story.append(Paragraph("5. <b>Candidate Profile Preservation:</b> Extracts the candidate's real name and header directly from their document, preserving authentic education and credentials.", bullet_style))

    story.append(Spacer(1, 10))

    # 7. Frontend User Experience
    story.append(Paragraph("6. Frontend UI/UX Architecture & Workflow", h1_style))
    story.append(Paragraph(
        "The React single-page application features a streamlined, high-aesthetic layout:",
        body_style
    ))
    story.append(Paragraph("• <b>Centered Branding Header:</b> Glowing ResuMatch ATS logo and title centered at the top.", bullet_style))
    story.append(Paragraph("• <b>Upload-Only Candidate Resume:</b> Drag-and-drop file upload with format badges (.PDF, .DOCX, .TXT). Manual typing is disabled on the candidate resume panel to ensure ATS parsing fidelity.", bullet_style))
    story.append(Paragraph("• <b>Target Job Description Input:</b> Direct textarea allowing recruiters or candidates to paste JD requirements.", bullet_style))
    story.append(Paragraph("• <b>Vector Resonance & Keyword Matrix:</b> Shows point-by-point requirement matches with vector similarity percentages and color-coded status pills (green, amber, rose).", bullet_style))
    story.append(Paragraph("• <b>Direct Export Actions:</b> One-click Word document download (.docx), clipboard copy, and print-to-PDF without needing an intermediary manual editor.", bullet_style))

    story.append(Spacer(1, 10))

    # 8. REST API Specifications
    story.append(Paragraph("7. REST API Endpoints Specification", h1_style))
    api_data = [
        [Paragraph("Endpoint", table_header_style), Paragraph("Method", table_header_style), Paragraph("Payload / Parameters", table_header_style), Paragraph("Response", table_header_style)],
        [
            Paragraph("<code>/api/parse-resume</code>", table_cell_style),
            Paragraph("POST", table_cell_style),
            Paragraph("Multipart form file (PDF, DOCX, TXT)", table_cell_style),
            Paragraph("JSON with extracted text, contact metadata, detected sections.", table_cell_style)
        ],
        [
            Paragraph("<code>/api/analyze-ats</code>", table_cell_style),
            Paragraph("POST", table_cell_style),
            Paragraph("JSON: <code>{ resume_text, job_description }</code>", table_cell_style),
            Paragraph("JSON with overall ATS score, vector analysis, keyword breakdown, checklist.", table_cell_style)
        ],
        [
            Paragraph("<code>/api/optimize-resume</code>", table_cell_style),
            Paragraph("POST", table_cell_style),
            Paragraph("JSON: <code>{ resume_text, job_description }</code>", table_cell_style),
            Paragraph("JSON with tailored summary, STAR bullets, updated resume, projected score.", table_cell_style)
        ],
        [
            Paragraph("<code>/api/export-docx</code>", table_cell_style),
            Paragraph("POST", table_cell_style),
            Paragraph("JSON: <code>{ resume_text, filename }</code>", table_cell_style),
            Paragraph("Binary attachment stream of ATS-formatted .docx document.", table_cell_style)
        ],
        [
            Paragraph("<code>/api/health</code>", table_cell_style),
            Paragraph("GET", table_cell_style),
            Paragraph("None", table_cell_style),
            Paragraph("JSON health status: <code>{ status: 'healthy' }</code>", table_cell_style)
        ],
    ]
    api_table = Table(api_data, colWidths=[105, 45, 170, 184])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, card_bg]),
    ]))
    story.append(api_table)

    # Build Document with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    return pdf_path

if __name__ == "__main__":
    out_pdf = build_pdf()
    print(f"Generated PDF successfully: {out_pdf}")
