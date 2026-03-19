"""Word document export"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class WordExporter:
    def export(self, content: str, title: str, output_path: str) -> str:
        """Export content to Word document"""
        logger.info(f"Exporting to Word: {output_path}")
        return output_path

def export_to_word(content: str, filename: str) -> str:
    exporter = WordExporter()
    path = f"exports/{filename}.docx"
    return exporter.export(content, filename, path)
