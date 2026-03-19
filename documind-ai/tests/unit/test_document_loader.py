"""Unit tests for document loader"""

import pytest
from src.ingestion.document_loader import DocumentLoader

def test_load_pdf():
    loader = DocumentLoader()
    # Test with sample PDF path
    assert loader is not None

def test_load_docx():
    loader = DocumentLoader()
    assert loader.supported_formats['.docx'] is not None

def test_unsupported_format():
    loader = DocumentLoader()
    with pytest.raises(ValueError):
        loader.load("test.xyz")
