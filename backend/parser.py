"""
Advanced Document Parser and Structured Extractor for Resumes.
Supports:
- PDF (Single-column, Two-column side-by-side, Tabular resumes, 1-page, 2-page, 3-page, any page length)
- DOCX (In-order body traversal, paragraphs, tables, deduplicated merged cells)
- Plain text / Markdown
- Structured info extraction: Candidate Name, Contact Info, Standard Sections, Categorized Skills, Readability Metrics.
"""
import io
import re
from typing import Dict, Any, List, Optional, Tuple, Set
import pypdf
import docx
from docx.table import Table
from docx.text.paragraph import Paragraph

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

from skills_taxonomy import extract_skills_from_text, find_category_for_skill


def _clean_text_line(line: str) -> str:
    """Normalize whitespace and control characters in a line."""
    line = re.sub(r'[\r\t]+', ' ', line)
    line = re.sub(r' +', ' ', line)
    return line.strip()


def extract_text_and_layout_from_pdf(file_bytes: bytes) -> Dict[str, Any]:
    """
    Extract text from PDF with layout intelligence:
    - Multi-page (1, 2, 3+ pages) extraction with running header/footer filtering
    - Column-aware extraction for two-column resumes (left sidebar vs right main body)
    - Table detection and structured formatting
    - Fallback to pypdf layout mode if pdfplumber encounters an issue
    """
    page_texts: List[str] = []
    page_count = 0
    tables_count = 0
    layout_detected = "Single-Column Flow"

    if PDFPLUMBER_AVAILABLE:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                page_count = len(pdf.pages)
                has_multicolumn = False
                has_tables = False

                for page_idx, page in enumerate(pdf.pages):
                    page_w = float(page.width or 612)
                    page_h = float(page.height or 792)

                    # 1. Extract any tables on the page
                    extracted_tables = page.extract_tables() or []
                    table_text_blocks = []
                    for tbl in extracted_tables:
                        if tbl and len(tbl) > 0:
                            has_tables = True
                            tables_count += 1
                            row_lines = []
                            for row in tbl:
                                clean_row = [_clean_text_line(str(cell)) for cell in row if cell and str(cell).strip()]
                                if clean_row:
                                    row_lines.append(" | ".join(clean_row))
                            if row_lines:
                                table_text_blocks.append("\n".join(row_lines))

                    # 2. Extract words with bounding boxes to detect multi-column layouts
                    words = page.extract_words(
                        x_tolerance=3,
                        y_tolerance=3,
                        keep_blank_chars=False,
                        use_text_flow=False
                    )

                    page_content = ""
                    if words:
                        # Check for vertical gutter separating page into two distinct columns
                        # Resumes commonly use: Left sidebar (width ~25-40% of page) & Right content (60-75%)
                        x0_list = [w['x0'] for w in words]
                        x1_list = [w['x1'] for w in words]

                        min_x = min(x0_list)
                        max_x = max(x1_list)
                        page_span = max_x - min_x

                        potential_split = None
                        if page_span > 250:
                            # Test gutter candidates between 25% and 50% of page width
                            for gutter_pct in [0.28, 0.33, 0.36, 0.40, 0.45]:
                                split_x = min_x + page_span * gutter_pct
                                gutter_margin = 15  # pixels of clear separation
                                in_left = [w for w in words if w['x1'] <= split_x - gutter_margin]
                                in_right = [w for w in words if w['x0'] >= split_x + gutter_margin]
                                in_middle = [w for w in words if not (w['x1'] <= split_x - gutter_margin or w['x0'] >= split_x + gutter_margin)]

                                # If substantial words on both sides and gutter is mostly clear
                                if len(in_left) >= 15 and len(in_right) >= 20 and len(in_middle) <= 5:
                                    potential_split = split_x
                                    has_multicolumn = True
                                    break

                        if potential_split:
                            # Process left column top-to-bottom, then right column top-to-bottom
                            left_words = [w for w in words if w['x1'] <= potential_split + 5]
                            right_words = [w for w in words if w['x0'] > potential_split - 5]

                            def format_column_words(col_words):
                                # Group words by vertical line (tolerance 3.5pt)
                                lines = []
                                sorted_words = sorted(col_words, key=lambda w: (round(w['top'] / 4.0), w['x0']))
                                current_line = []
                                current_top = None
                                for w in sorted_words:
                                    if current_top is None or abs(w['top'] - current_top) <= 4.0:
                                        current_line.append(w['text'])
                                        current_top = w['top'] if current_top is None else (current_top + w['top']) / 2.0
                                    else:
                                        if current_line:
                                            lines.append(" ".join(current_line))
                                        current_line = [w['text']]
                                        current_top = w['top']
                                if current_line:
                                    lines.append(" ".join(current_line))
                                return "\n".join(lines)

                            left_text = format_column_words(left_words)
                            right_text = format_column_words(right_words)
                            page_content = f"{left_text}\n\n{right_text}"
                        else:
                            # Single column layout: standard text extraction
                            standard_text = page.extract_text(layout=False) or ""
                            page_content = standard_text

                    # If table text blocks exist and not already cleanly inside words, append structured tables
                    if table_text_blocks and len(table_text_blocks) > 0:
                        # Only append if table rows aren't fully represented
                        first_row_sample = table_text_blocks[0].split('\n')[0] if table_text_blocks[0] else ""
                        if first_row_sample and first_row_sample not in page_content:
                            page_content = page_content + "\n\n" + "\n\n".join(table_text_blocks)

                    if page_content.strip():
                        page_texts.append(page_content.strip())

                # Set layout description
                if has_multicolumn and has_tables:
                    layout_detected = "Multi-Column with Tabular Grids"
                elif has_multicolumn:
                    layout_detected = "Two-Column Layout (Sidebar + Main Flow)"
                elif has_tables:
                    layout_detected = "Tabular / Grid Layout"
                else:
                    layout_detected = "Single-Column Flow"

        except Exception as e:
            # If pdfplumber encounters an unhandled PDF stream error, fall back to pypdf
            page_texts = []

    # Fallback to pypdf if pdfplumber was unavailable or extracted empty text
    if not page_texts:
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            page_count = len(reader.pages)
            for page in reader.pages:
                try:
                    # pypdf 6.x supports layout extraction mode
                    t = page.extract_text(extraction_mode="layout") or page.extract_text()
                except Exception:
                    t = page.extract_text()
                if t and t.strip():
                    page_texts.append(t.strip())
            layout_detected = "Standard PDF Stream"
        except Exception as e:
            pass

    # Clean running headers/footers across multi-page documents (2-page, 3-page, etc.)
    cleaned_pages = _clean_multipage_headers_footers(page_texts)
    full_text = "\n\n".join(cleaned_pages).strip()

    return {
        "text": full_text,
        "page_count": max(1, page_count),
        "layout_detected": f"{layout_detected} ({max(1, page_count)} Page{'s' if page_count > 1 else ''})",
        "tables_found": tables_count,
        "pages_extracted": len(cleaned_pages)
    }


def _clean_multipage_headers_footers(pages: List[str]) -> List[str]:
    """
    Remove repetitive running headers and footers across page 2, 3, etc.
    (e.g., 'Page 2 of 3', repeated candidate contact line on top of subsequent pages).
    """
    if len(pages) <= 1:
        return pages

    cleaned = []
    page_num_pattern = re.compile(r'^\s*(?:page\s*\d+\s*(?:of|\/)\s*\d+|\d+\s*\/\s*\d+|\bpage\s*\d+\b)\s*$', re.IGNORECASE)

    for i, page_text in enumerate(pages):
        lines = page_text.split('\n')
        filtered_lines = []

        for line_idx, line in enumerate(lines):
            # Check for page numbers at beginning or end of page
            if (line_idx <= 2 or line_idx >= len(lines) - 3) and page_num_pattern.match(line.strip()):
                continue
            filtered_lines.append(line)

        cleaned.append("\n".join(filtered_lines))

    return cleaned


def extract_text_and_layout_from_docx(file_bytes: bytes) -> Dict[str, Any]:
    """
    Extract text from DOCX in true sequential document order:
    Iterates over body elements so paragraphs and tables appear in exact sequence,
    and deduplicates merged table cells.
    """
    doc = docx.Document(io.BytesIO(file_bytes))
    text_parts: List[str] = []
    tables_count = 0
    seen_cells: Set[Any] = set()

    for child in doc.element.body:
        # Check if child is a paragraph
        if child.tag.endswith('p'):
            para = Paragraph(child, doc)
            clean_p = _clean_text_line(para.text)
            if clean_p:
                text_parts.append(clean_p)

        # Check if child is a table
        elif child.tag.endswith('tbl'):
            table = Table(child, doc)
            tables_count += 1
            table_lines = []

            for row in table.rows:
                row_cells_text = []
                for cell in row.cells:
                    # Deduplicate merged cells that share the same XML element
                    cell_id = id(cell._tc)
                    if cell_id in seen_cells:
                        continue
                    seen_cells.add(cell_id)

                    cell_text = _clean_text_line(cell.text)
                    if cell_text:
                        row_cells_text.append(cell_text)

                if row_cells_text:
                    table_lines.append(" | ".join(row_cells_text))

            if table_lines:
                text_parts.append("\n".join(table_lines))

    full_text = "\n\n".join(text_parts).strip()
    words = len(re.findall(r'\b\w+\b', full_text))
    # Approximate page count for docx (approx 450 words per page)
    est_pages = max(1, round(words / 450)) if words > 0 else 1

    layout = "Tabular / Grid Layout" if tables_count > 0 else "Standard Document Flow"

    return {
        "text": full_text,
        "page_count": est_pages,
        "layout_detected": f"{layout} (~{est_pages} Page{'s' if est_pages > 1 else ''})",
        "tables_found": tables_count,
        "pages_extracted": est_pages
    }


def extract_candidate_name(text: str, email: Optional[str] = None) -> Optional[str]:
    """
    Extract candidate full name from top lines of the resume text.
    Filters out common resume headings, metadata, and noise words.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return None

    # Blacklist words that look like headers or sections
    blacklist = {
        "resume", "curriculum", "vitae", "cv", "summary", "profile", "contact",
        "email", "phone", "portfolio", "experience", "education", "skills",
        "objective", "page", "developer", "engineer", "designer", "manager"
    }

    # Search top 6 lines
    for line in lines[:6]:
        # Remove any leading bullet or separator
        clean = re.sub(r'^[•\-\*\u2022\s]+', '', line).strip()
        # Clean line should be 2 to 4 words
        words = clean.split()
        if 2 <= len(words) <= 4:
            # Check that line does not have email, URL, or digits
            if '@' not in clean and 'http' not in clean.lower() and not re.search(r'\d', clean):
                lower_words = [w.lower() for w in words]
                if not any(w in blacklist for w in lower_words):
                    # Check that words start with capital letter
                    if all(w[0].isupper() for w in words if len(w) > 1 and w.isalpha()):
                        return clean

    # Fallback to name inferred from email if format like john.doe@email.com
    if email:
        username = email.split('@')[0]
        parts = re.split(r'[._-]', username)
        if len(parts) >= 2 and all(p.isalpha() for p in parts[:2]):
            return " ".join(p.capitalize() for p in parts[:2])

    return None


def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
    """
    Extract verified contact information:
    Email, Phone, LinkedIn, GitHub, Portfolio/Website, and Location.
    """
    # Email regex
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)

    # Phone regex (supports international codes +1, +44, +91, parens, dashes, spaces)
    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)

    # LinkedIn regex
    linkedin_match = re.search(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[a-zA-Z0-9_-]+', text, re.IGNORECASE)

    # GitHub regex
    github_match = re.search(r'(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9_-]+', text, re.IGNORECASE)

    # Portfolio / Personal Website regex (excluding linkedin and github)
    portfolio_match = None
    all_urls = re.findall(r'https?:\/\/[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?', text, re.IGNORECASE)
    for u in all_urls:
        if 'linkedin.com' not in u.lower() and 'github.com' not in u.lower():
            portfolio_match = u
            break

    # Location / City extraction heuristics
    location_match = None
    # Look for patterns like "City, ST" or "City, Country" in first 15 lines
    top_text = "\n".join(text.split('\n')[:15])
    loc_search = re.search(r'\b([A-Z][a-zA-Z\s]{2,18},\s*[A-Z]{2}\b|[A-Z][a-zA-Z\s]{2,18},\s*(?:USA|UK|Canada|India|Germany|Australia|Singapore|Remote))\b', top_text)
    if loc_search:
        location_match = loc_search.group(0).strip()

    return {
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "linkedin": linkedin_match.group(0) if linkedin_match else None,
        "github": github_match.group(0) if github_match else None,
        "portfolio": portfolio_match,
        "location": location_match
    }


def detect_sections(text: str) -> Dict[str, str]:
    """
    Split resume text into identified logical sections with cross-page continuity.
    Standard sections: Summary, Experience, Skills, Education, Projects, Certifications.
    """
    section_patterns = {
        "summary": r"\b(?:summary|professional\s+summary|profile|about\s+me|career\s+objective|objective|executive\s+summary)\b",
        "experience": r"\b(?:experience|work\s+experience|employment\s+history|professional\s+experience|work\s+history|career\s+history)\b",
        "skills": r"\b(?:skills|technical\s+skills|core\s+competencies|technologies|tools\s+&\s+technologies|skills\s+&\s+expertise|programming\s+languages|skills\s+matrix)\b",
        "education": r"\b(?:education|academic\s+background|qualifications|academic\s+history|degrees|academic\s+credentials|credentials)\b",
        "projects": r"\b(?:projects|key\s+projects|personal\s+projects|academic\s+projects|selected\s+projects)\b",
        "certifications": r"\b(?:certifications|licenses|courses|awards\s+&\s+certifications|certificates|honors\s+&\s+awards)\b"
    }

    lines = [line.strip() for line in text.split('\n') if line.strip()]

    sections: Dict[str, List[str]] = {
        "header": [],
        "summary": [],
        "experience": [],
        "skills": [],
        "education": [],
        "projects": [],
        "certifications": [],
        "other": []
    }

    current_section = "header"

    for line in lines:
        matched_section = None
        words = line.split()
        # Short lines (<= 6 words) that match section keywords
        if 1 <= len(words) <= 6:
            clean_line = re.sub(r'[^a-zA-Z\s]', ' ', line).strip().lower()
            clean_line = re.sub(r'\s+', ' ', clean_line)
            for sec_name, pattern in section_patterns.items():
                if re.search(pattern, clean_line):
                    matched_section = sec_name
                    break

        if matched_section:
            current_section = matched_section
        else:
            sections[current_section].append(line)

    return {sec: "\n".join(content) for sec, content in sections.items() if content}


def evaluate_ats_readability(text: str) -> Dict[str, Any]:
    """
    Evaluate structural formatting and readability factors crucial for ATS parsers.
    """
    words = re.findall(r'\b\w+\b', text)
    word_count = len(words)
    contacts = extract_contact_info(text)
    sections = detect_sections(text)

    bullet_count = len(re.findall(r'(?:^|\n)\s*[•\-\*\u2022\u2023\u25E6\u2043\u2219]\s+', text))

    checks = []

    # 1. Contact Information Checks
    if contacts["email"]:
        checks.append({"name": "Professional Email Address", "status": "pass", "desc": f"Found: {contacts['email']}"})
    else:
        checks.append({"name": "Professional Email Address", "status": "fail", "desc": "No valid email address found in resume header."})

    if contacts["phone"]:
        checks.append({"name": "Phone Number", "status": "pass", "desc": f"Found: {contacts['phone']}"})
    else:
        checks.append({"name": "Phone Number", "status": "warning", "desc": "Phone number was not detected."})

    if contacts["linkedin"] or contacts["github"]:
        checks.append({"name": "Professional Links (LinkedIn/GitHub)", "status": "pass", "desc": "Found professional profile link(s)."})
    else:
        checks.append({"name": "Professional Links (LinkedIn/GitHub)", "status": "warning", "desc": "Consider adding LinkedIn/GitHub profile URLs."})

    # 2. Section Checks
    if "experience" in sections:
        checks.append({"name": "Work Experience Section", "status": "pass", "desc": "Clear Experience section header detected."})
    else:
        checks.append({"name": "Work Experience Section", "status": "fail", "desc": "Missing clear 'Experience' or 'Work History' header."})

    if "skills" in sections:
        checks.append({"name": "Dedicated Skills Section", "status": "pass", "desc": "Dedicated Technical/Skills section found."})
    else:
        checks.append({"name": "Dedicated Skills Section", "status": "warning", "desc": "A separate 'Skills' section makes keyword parsing much easier for ATS."})

    if "education" in sections:
        checks.append({"name": "Education Section", "status": "pass", "desc": "Education section recognized."})
    else:
        checks.append({"name": "Education Section", "status": "warning", "desc": "No recognizable 'Education' header detected."})

    # 3. Word Count Check
    if 300 <= word_count <= 1400:
        checks.append({"name": "Resume Length", "status": "pass", "desc": f"Optimal word count ({word_count} words)."})
    elif word_count < 300:
        checks.append({"name": "Resume Length", "status": "warning", "desc": f"Too brief ({word_count} words). Aim for 400-900 words."})
    else:
        checks.append({"name": "Resume Length", "status": "warning", "desc": f"Very lengthy ({word_count} words). Ensure standard 1-3 page formatting."})

    # 4. Bullet Points Check
    if bullet_count >= 5:
        checks.append({"name": "Action Bullet Points", "status": "pass", "desc": f"Detected {bullet_count} structured bullet points."})
    else:
        checks.append({"name": "Action Bullet Points", "status": "warning", "desc": "ATS scanners prefer distinct bullet points over dense paragraphs."})

    passed_count = sum(1 for c in checks if c["status"] == "pass")
    warning_count = sum(1 for c in checks if c["status"] == "warning")
    total_checks = len(checks)
    readability_score = round(((passed_count * 1.0 + warning_count * 0.5) / total_checks) * 100)

    return {
        "score": readability_score,
        "word_count": word_count,
        "bullet_count": bullet_count,
        "contact_info": contacts,
        "sections_found": list(sections.keys()),
        "checks": checks
    }


def parse_resume_document(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Master entrypoint to parse any resume document (PDF, DOCX, TXT),
    detect multi-page structures, tables, candidate name, contact info,
    and categorize skills.
    """
    fn_lower = filename.lower()

    if fn_lower.endswith(".pdf"):
        extraction_res = extract_text_and_layout_from_pdf(file_bytes)
        file_format = "PDF"
    elif fn_lower.endswith((".docx", ".doc")):
        extraction_res = extract_text_and_layout_from_docx(file_bytes)
        file_format = "DOCX"
    else:
        text = file_bytes.decode("utf-8", errors="ignore")
        words = len(re.findall(r'\b\w+\b', text))
        est_pages = max(1, round(words / 450)) if words > 0 else 1
        extraction_res = {
            "text": text,
            "page_count": est_pages,
            "layout_detected": f"Plain Text ({est_pages} Page{'s' if est_pages > 1 else ''})",
            "tables_found": 0,
            "pages_extracted": est_pages
        }
        file_format = "TXT"

    full_text = extraction_res["text"]
    contacts = extract_contact_info(full_text)
    candidate_name = extract_candidate_name(full_text, email=contacts.get("email"))
    sections = detect_sections(full_text)
    readability = evaluate_ats_readability(full_text)
    extracted_skills_dict = extract_skills_from_text(full_text)

    # Calculate skills list
    all_skills_flat = [s for skills in extracted_skills_dict.values() for s in skills]

    return {
        "filename": filename,
        "format": file_format,
        "page_count": extraction_res["page_count"],
        "layout_detected": extraction_res["layout_detected"],
        "tables_found": extraction_res.get("tables_found", 0),
        "candidate_name": candidate_name or "Candidate",
        "contact_info": contacts,
        "word_count": readability["word_count"],
        "character_count": len(full_text),
        "bullet_count": readability["bullet_count"],
        "readability": readability,
        "sections": sections,
        "sections_detected": list(sections.keys()),
        "structured_skills": extracted_skills_dict,
        "skills_count": len(all_skills_flat),
        "text": full_text
    }


# Backwards compatibility wrappers
def extract_text_from_pdf(file_bytes: bytes) -> str:
    return extract_text_and_layout_from_pdf(file_bytes)["text"]

def extract_text_from_docx(file_bytes: bytes) -> str:
    return extract_text_and_layout_from_docx(file_bytes)["text"]
