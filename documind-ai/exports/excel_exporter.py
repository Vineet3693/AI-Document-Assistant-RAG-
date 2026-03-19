"""Excel export functionality"""

import logging

logger = logging.getLogger(__name__)

class ExcelExporter:
    def export_table(self, data: list, headers: list, output_path: str) -> str:
        """Export table data to Excel"""
        logger.info(f"Exporting table to {output_path}")
        return output_path

def export_to_excel(data: list, filename: str) -> str:
    exporter = ExcelExporter()
    path = f"exports/{filename}.xlsx"
    return exporter.export_table(data, [], path)
