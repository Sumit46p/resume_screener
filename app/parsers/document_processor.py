"""
Unified Document Processor with automatic format detection and error handling.
"""
import os
from typing import Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .pdf_parser import parse_pdf, parse_pdf_from_bytes
from .docx_parser import parse_docx, parse_docx_from_bytes


class DocumentType(Enum):
    PDF = "pdf"
    DOCX = "docx"
    TEXT = "text"
    UNKNOWN = "unknown"


@dataclass
class ParseResult:
    """Result of document parsing."""
    success: bool
    text: str
    document_type: DocumentType
    error: Optional[str] = None
    filename: Optional[str] = None


class DocumentProcessor:
    """
    Unified processor for resume documents.
    Handles PDF, DOCX, and plain text with graceful error handling.
    """
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt'}
    
    @classmethod
    def process_file(cls, file_path: str) -> ParseResult:
        """
        Process a document file from disk.
        
        Args:
            file_path: Path to the document
            
        Returns:
            ParseResult with extracted text or error
        """
        filename = os.path.basename(file_path)
        doc_type = cls._detect_type_from_extension(file_path)
        
        if doc_type == DocumentType.UNKNOWN:
            return ParseResult(
                success=False,
                text="",
                document_type=doc_type,
                error=f"Unsupported file type: {os.path.splitext(file_path)[1]}",
                filename=filename
            )
        
        try:
            if doc_type == DocumentType.PDF:
                text = parse_pdf(file_path)
            elif doc_type == DocumentType.DOCX:
                text = parse_docx(file_path)
            elif doc_type == DocumentType.TEXT:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                text = ""
            
            return ParseResult(
                success=True,
                text=text,
                document_type=doc_type,
                filename=filename
            )
        except Exception as e:
            return ParseResult(
                success=False,
                text="",
                document_type=doc_type,
                error=str(e),
                filename=filename
            )
    
    @classmethod
    def process_bytes(cls, content: bytes, filename: str) -> ParseResult:
        """
        Process document from bytes (file upload).
        
        Args:
            content: File content as bytes
            filename: Original filename for type detection
            
        Returns:
            ParseResult with extracted text or error
        """
        doc_type = cls._detect_type_from_extension(filename)
        
        if doc_type == DocumentType.UNKNOWN:
            # Try to detect from content
            doc_type = cls._detect_type_from_content(content)
        
        if doc_type == DocumentType.UNKNOWN:
            return ParseResult(
                success=False,
                text="",
                document_type=doc_type,
                error=f"Could not determine file type for: {filename}",
                filename=filename
            )
        
        try:
            if doc_type == DocumentType.PDF:
                text = parse_pdf_from_bytes(content)
            elif doc_type == DocumentType.DOCX:
                text = parse_docx_from_bytes(content)
            elif doc_type == DocumentType.TEXT:
                text = content.decode('utf-8')
            else:
                text = ""
            
            return ParseResult(
                success=True,
                text=text,
                document_type=doc_type,
                filename=filename
            )
        except Exception as e:
            return ParseResult(
                success=False,
                text="",
                document_type=doc_type,
                error=str(e),
                filename=filename
            )
    
    @staticmethod
    def _detect_type_from_extension(filename: str) -> DocumentType:
        """Detect document type from file extension."""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == '.pdf':
            return DocumentType.PDF
        elif ext in ('.docx', '.doc'):
            return DocumentType.DOCX
        elif ext == '.txt':
            return DocumentType.TEXT
        else:
            return DocumentType.UNKNOWN
    
    @staticmethod
    def _detect_type_from_content(content: bytes) -> DocumentType:
        """Detect document type from content magic bytes."""
        if content.startswith(b'%PDF'):
            return DocumentType.PDF
        elif content.startswith(b'PK'):  # DOCX is a ZIP file
            return DocumentType.DOCX
        elif cls._is_likely_text(content):
            return DocumentType.TEXT
        else:
            return DocumentType.UNKNOWN
    
    @staticmethod
    def _is_likely_text(content: bytes) -> bool:
        """Check if content is likely plain text."""
        try:
            content.decode('utf-8')
            return True
        except:
            return False
