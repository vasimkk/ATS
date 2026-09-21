"""
ATS Document Exporter.
Creates cleanly formatted, ATS-compliant Microsoft Word (.docx) documents.
"""
import io
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_docx_from_text(resume_text: str, title: str = "ATS Optimized Resume") -> io.BytesIO:
    """
    Format and produce an ATS-clean .docx file.
    ATS Best Practices:
    - Standard 1-inch margins
    - Clean typography (Calibri / Arial)
    - Clear standard headings
    - Bullet points using native Word bullet styles
    """
    doc = docx.Document()
    
    # 1 inch margins for ATS
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
    lines = resume_text.split('\n')
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        # Ignore cosmetic separator lines
        if set(line_str).issubset({'=', '-', '_', '*'}):
            continue
            
        # Check if title line (first header)
        if line_str.startswith("PROFESSIONAL RESUME"):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(line_str)
            run.bold = True
            run.font.size = Pt(16)
            run.font.name = "Arial"
            run.font.color.rgb = RGBColor(24, 43, 73)
            
        # Check if contact line
        elif "@" in line_str and ("|" in line_str or "Phone" in line_str):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(line_str)
            run.font.size = Pt(10)
            run.font.name = "Arial"
            run.font.color.rgb = RGBColor(100, 116, 139)
            
        # Major Section Headings (All caps)
        elif line_str.isupper() and len(line_str.split()) <= 6:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(line_str)
            run.bold = True
            run.font.size = Pt(12)
            run.font.name = "Arial"
            run.font.color.rgb = RGBColor(15, 23, 42)
            
        # Bullet items
        elif line_str.startswith(('•', '-', '*')):
            clean_bullet = line_str.lstrip('•-* ').strip()
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(clean_bullet)
            run.font.size = Pt(10.5)
            run.font.name = "Arial"
            
        # Standard body text
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(line_str)
            run.font.size = Pt(10.5)
            run.font.name = "Arial"
            
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream
