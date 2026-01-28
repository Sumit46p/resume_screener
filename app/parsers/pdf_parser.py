"""
PDF Parser with robust text extraction supporting multiple layouts.
"""
import io
from typing import Optional
from pypdf import PdfReader


def parse_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text from all pages
    """
    try:
        reader = PdfReader(file_path)
        return _extract_text_from_reader(reader)
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")


def parse_pdf_from_bytes(content: bytes) -> str:
    """
    Extract text from PDF bytes (for file uploads).
    
    Args:
        content: PDF file content as bytes
        
    Returns:
        Extracted text from all pages
    """
    try:
        reader = PdfReader(io.BytesIO(content))
        return _extract_text_from_reader(reader)
    except Exception as e:
        raise ValueError(f"Failed to parse PDF from bytes: {str(e)}")


def _extract_text_from_reader(reader: PdfReader) -> str:
    """
    Extract and clean text from a PDF reader object.
    Handles multi-column layouts and tables.
    """
    text_parts = []
    
    for page in reader.pages:
        try:
            page_text = page.extract_text()
            if page_text:
                # Clean up the text
                cleaned = _clean_extracted_text(page_text)
                text_parts.append(cleaned)
        except Exception:
            # Skip pages that fail to parse
            continue
    
    full_text = "\n\n".join(text_parts)
    return _normalize_whitespace(full_text)


def _clean_extracted_text(text: str) -> str:
    """
    Clean extracted text by fixing common issues.
    """
    # Fix common extraction artifacts
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            # Skip lines that are just numbers (page numbers)
            if line.isdigit():
                continue
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def _normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in extracted text.
    """
    # Replace multiple spaces with single space
    import re
    text = re.sub(r' +', ' ', text)
    # Replace multiple newlines with double newline (section separator)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
