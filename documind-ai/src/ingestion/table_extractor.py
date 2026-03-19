"""
Table Extractor Module
Extract tables from PDFs and Word documents
"""

from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TableExtractor:
    """
    Extract tables from documents
    
    Supports:
    - PDF tables (using Camelot, pdfplumber, tabula)
    - Word document tables (using python-docx)
    - Excel sheets (using pandas)
    
    Output formats:
    - CSV
    - Markdown
    - HTML
    - JSON
    """
    
    def __init__(self, backend: str = "pdfplumber"):
        """
        Initialize table extractor
        
        Args:
            backend: Backend to use ("pdfplumber", "camelot", "tabula")
        """
        self.backend = backend
        self._initialized = False
        
    def _initialize(self):
        """Initialize the extraction backend"""
        if self._initialized:
            return
            
        if self.backend == "pdfplumber":
            try:
                import pdfplumber
                self._initialized = True
                logger.info("pdfplumber initialized successfully")
            except ImportError:
                logger.error("pdfplumber not installed. Run: pip install pdfplumber")
                raise
                
        elif self.backend == "camelot":
            try:
                import camelot
                self._initialized = True
                logger.info("Camelot initialized successfully")
            except ImportError:
                logger.error("camelot not installed. Run: pip install camelot-py[cv]")
                raise
                
        elif self.backend == "tabula":
            try:
                import tabula
                self._initialized = True
                logger.info("Tabula-py initialized successfully")
            except ImportError:
                logger.error("tabula-py not installed. Run: pip install tabula-py")
                raise
        else:
            raise ValueError(f"Unknown backend: {self.backend}")
    
    def extract_from_pdf(
        self,
        pdf_path: Union[str, Path],
        pages: Optional[List[int]] = None,
        flavor: str = "lattice"
    ) -> List[Dict[str, Any]]:
        """
        Extract tables from a PDF file
        
        Args:
            pdf_path: Path to PDF file
            pages: List of page numbers to process (None = all)
            flavor: Extraction mode ("lattice" for bordered tables, "stream" for borderless)
            
        Returns:
            List of dictionaries with table data and metadata
        """
        self._initialize()
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        logger.info(f"Extracting tables from PDF: {pdf_path}")
        
        if self.backend == "pdfplumber":
            return self._extract_with_pdfplumber(pdf_path, pages, flavor)
        elif self.backend == "camelot":
            return self._extract_with_camelot(pdf_path, pages, flavor)
        elif self.backend == "tabula":
            return self._extract_with_tabula(pdf_path, pages, flavor)
        else:
            raise ValueError(f"Unknown backend: {self.backend}")
    
    def _extract_with_pdfplumber(
        self,
        pdf_path: Path,
        pages: Optional[List[int]],
        flavor: str
    ) -> List[Dict[str, Any]]:
        """Extract tables using pdfplumber"""
        import pdfplumber
        
        tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            page_nums = pages if pages else range(len(pdf.pages))
            
            for page_num in page_nums:
                if page_num >= len(pdf.pages):
                    continue
                    
                page = pdf.pages[page_num]
                page_tables = page.extract_tables()
                
                for table_idx, table_data in enumerate(page_tables):
                    if not table_data:
                        continue
                    
                    # Convert to list of lists
                    rows = []
                    for row in table_data:
                        cleaned_row = [str(cell).strip() if cell is not None else "" for cell in row]
                        rows.append(cleaned_row)
                    
                    if rows:
                        tables.append({
                            'page_number': page_num + 1,
                            'table_index': table_idx,
                            'data': rows,
                            'num_rows': len(rows),
                            'num_cols': max(len(row) for row in rows) if rows else 0,
                            'format': '2d_array'
                        })
        
        logger.info(f"Found {len(tables)} tables in PDF")
        return tables
    
    def _extract_with_camelot(
        self,
        pdf_path: Path,
        pages: Optional[List[int]],
        flavor: str
    ) -> List[Dict[str, Any]]:
        """Extract tables using Camelot"""
        import camelot
        
        # Build page string for camelot
        if pages:
            page_str = ','.join(str(p) for p in pages)
        else:
            page_str = 'all'
        
        try:
            # Try lattice flavor first (for bordered tables)
            tables = camelot.read_pdf(
                str(pdf_path),
                pages=page_str,
                flavor='lattice',
                suppress_stdout=True
            )
        except Exception:
            # Fall back to stream flavor (for borderless tables)
            tables = camelot.read_pdf(
                str(pdf_path),
                pages=page_str,
                flavor='stream',
                suppress_stdout=True
            )
        
        result = []
        for table in tables:
            df = table.df
            result.append({
                'page_number': table.page,
                'table_index': table.order,
                'data': df.values.tolist(),
                'num_rows': len(df),
                'num_cols': len(df.columns),
                'accuracy': table.parsing_report.get('accuracy', 0),
                'format': '2d_array'
            })
        
        logger.info(f"Found {len(result)} tables with Camelot")
        return result
    
    def _extract_with_tabula(
        self,
        pdf_path: Path,
        pages: Optional[List[int]],
        flavor: str
    ) -> List[Dict[str, Any]]:
        """Extract tables using Tabula"""
        import tabula
        import pandas as pd
        
        # Build page string for tabula
        if pages:
            page_str = ','.join(str(p) for p in pages)
        else:
            page_str = 'all'
        
        # Extract tables as DataFrames
        dfs = tabula.read_pdf(
            str(pdf_path),
            pages=page_str,
            multiple_tables=True,
            lattice=(flavor == 'lattice'),
            stream=(flavor == 'stream')
        )
        
        result = []
        for idx, df in enumerate(dfs):
            if df.empty:
                continue
                
            result.append({
                'page_number': idx + 1,  # Tabula doesn't provide exact page
                'table_index': idx,
                'data': df.values.tolist(),
                'num_rows': len(df),
                'num_cols': len(df.columns),
                'columns': df.columns.tolist(),
                'format': '2d_array'
            })
        
        logger.info(f"Found {len(result)} tables with Tabula")
        return result
    
    def extract_from_docx(
        self,
        docx_path: Union[str, Path]
    ) -> List[Dict[str, Any]]:
        """
        Extract tables from a Word document
        
        Args:
            docx_path: Path to .docx file
            
        Returns:
            List of dictionaries with table data
        """
        from docx import Document
        
        docx_path = Path(docx_path)
        
        if not docx_path.exists():
            raise FileNotFoundError(f"DOCX not found: {docx_path}")
        
        logger.info(f"Extracting tables from DOCX: {docx_path}")
        
        doc = Document(docx_path)
        tables = []
        
        for idx, table in enumerate(doc.tables):
            rows = []
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                rows.append(row_data)
            
            if rows:
                tables.append({
                    'table_index': idx,
                    'data': rows,
                    'num_rows': len(rows),
                    'num_cols': len(rows[0]) if rows else 0,
                    'format': '2d_array'
                })
        
        logger.info(f"Found {len(tables)} tables in DOCX")
        return tables
    
    def extract_from_excel(
        self,
        excel_path: Union[str, Path],
        sheet_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract tables from an Excel file
        
        Args:
            excel_path: Path to Excel file (.xlsx, .xls)
            sheet_name: Specific sheet name (None = all sheets)
            
        Returns:
            List of dictionaries with table data
        """
        import pandas as pd
        
        excel_path = Path(excel_path)
        
        if not excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {excel_path}")
        
        logger.info(f"Extracting tables from Excel: {excel_path}")
        
        # Get all sheet names
        xls = pd.ExcelFile(excel_path)
        sheet_names = [sheet_name] if sheet_name else xls.sheet_names
        
        tables = []
        for sheet in sheet_names:
            try:
                df = pd.read_excel(excel_path, sheet_name=sheet)
                
                if not df.empty:
                    tables.append({
                        'sheet_name': sheet,
                        'data': df.values.tolist(),
                        'num_rows': len(df),
                        'num_cols': len(df.columns),
                        'columns': df.columns.tolist(),
                        'format': '2d_array'
                    })
            except Exception as e:
                logger.warning(f"Error reading sheet {sheet}: {e}")
        
        logger.info(f"Found {len(tables)} tables in Excel")
        return tables
    
    def table_to_csv(self, table_data: List[List[str]]) -> str:
        """Convert table data to CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(table_data)
        return output.getvalue()
    
    def table_to_markdown(self, table_data: List[List[str]]) -> str:
        """Convert table data to Markdown format"""
        if not table_data:
            return ""
        
        lines = []
        
        # Header row
        header = table_data[0]
        lines.append("| " + " | ".join(header) + " |")
        
        # Separator row
        lines.append("| " + " | ".join(["---"] * len(header)) + " |")
        
        # Data rows
        for row in table_data[1:]:
            # Pad row if needed
            padded_row = row + [""] * (len(header) - len(row))
            lines.append("| " + " | ".join(padded_row) + " |")
        
        return "\n".join(lines)
    
    def table_to_html(self, table_data: List[List[str]]) -> str:
        """Convert table data to HTML format"""
        if not table_data:
            return "<table></table>"
        
        html = ["<table>"]
        
        # Header
        html.append("  <thead>")
        html.append("    <tr>")
        for cell in table_data[0]:
            html.append(f"      <th>{cell}</th>")
        html.append("    </tr>")
        html.append("  </thead>")
        
        # Body
        html.append("  <tbody>")
        for row in table_data[1:]:
            html.append("    <tr>")
            for cell in row:
                html.append(f"      <td>{cell}</td>")
            html.append("    </tr>")
        html.append("  </tbody>")
        
        html.append("</table>")
        return "\n".join(html)
    
    def table_to_text(self, table_data: List[List[str]], max_width: int = 20) -> str:
        """Convert table data to formatted text"""
        if not table_data:
            return ""
        
        # Calculate column widths
        num_cols = max(len(row) for row in table_data)
        col_widths = [max_width] * num_cols
        
        for row in table_data:
            for i, cell in enumerate(row):
                col_widths[i] = min(max(col_widths[i], len(str(cell))), max_width)
        
        # Format rows
        lines = []
        separator = "+" + "+".join("-" * w for w in col_widths) + "+"
        
        for row in table_data:
            padded_row = row + [""] * (num_cols - len(row))
            cells = [str(cell).ljust(w)[:w] for cell, w in zip(padded_row, col_widths)]
            lines.append("|" + "|".join(cells) + "|")
            if lines.index("|" + "|".join(cells) + "|") == 0:
                lines.insert(1, separator)
        
        lines.insert(0, separator)
        lines.append(separator)
        
        return "\n".join(lines)


def extract_tables(
    file_path: Union[str, Path],
    output_format: str = "markdown"
) -> List[str]:
    """
    Convenience function to extract tables from any supported file
    
    Args:
        file_path: Path to document
        output_format: Desired output format ("csv", "markdown", "html", "text")
        
    Returns:
        List of table strings in specified format
    """
    file_path = Path(file_path)
    extractor = TableExtractor()
    tables = []
    
    suffix = file_path.suffix.lower()
    
    if suffix == '.pdf':
        table_data = extractor.extract_from_pdf(file_path)
    elif suffix == '.docx':
        table_data = extractor.extract_from_docx(file_path)
    elif suffix in ['.xlsx', '.xls']:
        table_data = extractor.extract_from_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
    
    # Convert to requested format
    converter = getattr(extractor, f'table_to_{output_format}', extractor.table_to_markdown)
    
    for table in table_data:
        tables.append(converter(table['data']))
    
    return tables
