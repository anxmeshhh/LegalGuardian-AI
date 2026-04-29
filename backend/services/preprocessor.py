"""
LegalGuardian AI — Text Preprocessing & Clause Segmentation

Handles:
- Text extraction from PDF, DOCX, and raw text
- Contract segmentation into individual clauses
- Text cleaning and normalization
"""

import re
import io
from typing import List, Dict, Optional


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text content from a PDF file."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text content from a DOCX file."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract text from DOCX: {str(e)}")


def extract_text(content: str, file_bytes: Optional[bytes] = None, 
                 file_type: Optional[str] = None) -> str:
    """
    Extract text from various input formats.
    
    Args:
        content: Raw text content (if pasted directly)
        file_bytes: File content as bytes (if uploaded)
        file_type: File MIME type or extension
    
    Returns:
        Extracted plain text
    """
    if file_bytes and file_type:
        if "pdf" in file_type.lower():
            return extract_text_from_pdf(file_bytes)
        elif "docx" in file_type.lower() or "word" in file_type.lower():
            return extract_text_from_docx(file_bytes)
        else:
            # Try to decode as plain text
            try:
                return file_bytes.decode("utf-8").strip()
            except UnicodeDecodeError:
                return file_bytes.decode("latin-1").strip()
    
    return clean_text(content)


def clean_text(text: str) -> str:
    """Clean and normalize contract text."""
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Normalize spaces
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove page numbers and headers/footers patterns
    text = re.sub(r'\n\s*Page \d+ of \d+\s*\n', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'\n\s*-\s*\d+\s*-\s*\n', '\n', text)
    # Strip leading/trailing whitespace per line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    return text.strip()


def segment_clauses(text: str) -> List[Dict]:
    """
    Segment a contract into individual clauses.
    
    Uses a multi-strategy approach:
    1. Section header detection (e.g., "Section 1.", "Article I", "1.")
    2. Paragraph-level fallback for unstructured text
    
    Returns:
        List of dicts with 'id', 'title', 'text', and 'section_number'
    """
    clauses = []
    
    # ─── Strategy 1: Section/Article header detection ─────────────────────
    # Matches patterns like:
    #   "Section 1. Title"
    #   "SECTION 1: Title"  
    #   "Article I. Title"
    #   "1. Title"
    #   "1.1 Title"
    #   "ARTICLE ONE"
    section_pattern = re.compile(
        r'(?:^|\n)\s*'
        r'(?:'
        r'(?:Section|SECTION|Article|ARTICLE|Clause|CLAUSE)\s+'  # Named sections
        r'(?:\d+(?:\.\d+)*|[IVXLC]+)\.?\s*'                      # Number or Roman numeral
        r'|'
        r'(?:\d+(?:\.\d+)*)\.?\s+'                                # Numbered sections (e.g., "1. ", "1.1 ")
        r')'
        r'(.*?)(?=\n)',                                            # Title text
        re.MULTILINE | re.IGNORECASE
    )
    
    matches = list(section_pattern.finditer(text))
    
    if len(matches) >= 3:  # Enough sections found to use this strategy
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            section_text = text[start:end].strip()
            
            # Extract title from the header line
            header_line = section_text.split('\n')[0].strip()
            title = _extract_section_title(header_line)
            
            # Get the body (everything after the header)
            body_lines = section_text.split('\n')[1:]
            body = '\n'.join(body_lines).strip()
            
            if body or title:  # Skip empty sections
                clauses.append({
                    "id": i + 1,
                    "title": title or f"Section {i + 1}",
                    "text": section_text,
                    "section_number": str(i + 1)
                })
    
    # ─── Strategy 2: Paragraph-based fallback ────────────────────────────
    if not clauses:
        paragraphs = re.split(r'\n\s*\n', text)
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if len(para) > 50:  # Skip very short paragraphs (titles, signatures)
                # Try to extract a title from the first line
                lines = para.split('\n')
                first_line = lines[0].strip()
                
                if len(first_line) < 100 and len(lines) > 1:
                    title = first_line
                    body = '\n'.join(lines[1:]).strip()
                else:
                    title = f"Paragraph {i + 1}"
                    body = para
                
                clauses.append({
                    "id": len(clauses) + 1,
                    "title": title,
                    "text": para,
                    "section_number": str(len(clauses) + 1)
                })
    
    # ─── Handle preamble (text before first section) ─────────────────────
    if matches and len(matches) >= 3:
        preamble = text[:matches[0].start()].strip()
        if len(preamble) > 50:
            clauses.insert(0, {
                "id": 0,
                "title": "Preamble / Recitals",
                "text": preamble,
                "section_number": "0"
            })
            # Re-number
            for i, clause in enumerate(clauses):
                clause["id"] = i + 1
    
    return clauses


def _extract_section_title(header: str) -> str:
    """Extract clean title from a section header line."""
    # Remove section/article prefix and number
    title = re.sub(
        r'^(?:Section|SECTION|Article|ARTICLE|Clause|CLAUSE)\s+'
        r'(?:\d+(?:\.\d+)*|[IVXLC]+)\.?\s*[-:.]?\s*',
        '', header, flags=re.IGNORECASE
    )
    # Remove standalone number prefix
    title = re.sub(r'^\d+(?:\.\d+)*\.?\s*[-:.]?\s*', '', title)
    return title.strip()


def get_clause_sentences(clause_text: str) -> List[str]:
    """Split a clause into individual sentences for fine-grained analysis."""
    # Simple sentence splitting (avoids heavy spaCy dependency for basic use)
    # Handles common abbreviations in legal text
    text = clause_text
    # Protect common abbreviations
    abbreviations = ['Inc.', 'Corp.', 'Ltd.', 'LLC.', 'Dr.', 'Mr.', 'Mrs.', 'Ms.',
                     'Jr.', 'Sr.', 'vs.', 'etc.', 'e.g.', 'i.e.', 'No.', 'Sec.']
    for abbr in abbreviations:
        text = text.replace(abbr, abbr.replace('.', '<DOT>'))
    
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    
    # Restore dots
    sentences = [s.replace('<DOT>', '.').strip() for s in sentences]
    
    return [s for s in sentences if len(s) > 10]
