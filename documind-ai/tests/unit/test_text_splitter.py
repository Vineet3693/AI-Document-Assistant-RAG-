"""Unit tests for text splitter"""

import pytest
from src.ingestion.text_splitter import TextSplitter, SentenceSplitter

def test_split_text():
    splitter = TextSplitter(chunk_size=100, chunk_overlap=20)
    text = "This is a test sentence. " * 50
    chunks = splitter.split_text(text)
    assert len(chunks) > 0
    assert all(len(c) <= 120 for c in chunks)

def test_sentence_splitter():
    splitter = SentenceSplitter()
    text = "First sentence. Second sentence. Third sentence."
    chunks = splitter.split_text(text)
    assert len(chunks) >= 1
