"""
DocuMind AI - File Validator
Validates uploaded files for type, size, and integrity.
"""

import os
from pathlib import Path
from typing import Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum


class ValidationResult(Enum):
    """Possible validation results."""
    VALID = "valid"
    INVALID_EXTENSION = "invalid_extension"
    FILE_TOO_LARGE = "file_too_large"
    FILE_EMPTY = "file_empty"
    FILE_CORRUPTED = "file_corrupted"
    FILE_NOT_FOUND = "file_not_found"
    MALICIOUS_CONTENT = "malicious_content"


@dataclass
class ValidationReport:
    """Report from file validation."""
    is_valid: bool
    result: ValidationResult
    message: str
    filename: str
    file_size: int
    file_extension: str
    mime_type: Optional[str] = None


class FileValidator:
    """Validate uploaded files for security and compatibility."""
    
    # Allowed extensions
    ALLOWED_EXTENSIONS = {
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.txt': 'text/plain',
        '.csv': 'text/csv',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.md': 'text/markdown',
        '.json': 'application/json',
        '.xml': 'application/xml',
    }
    
    # Maximum file size in bytes (default 50MB)
    DEFAULT_MAX_SIZE = 50 * 1024 * 1024
    
    def __init__(self, max_size_mb: int = 50, custom_extensions: Optional[List[str]] = None):
        self.max_size = max_size_mb * 1024 * 1024
        self.allowed_extensions = custom_extensions or list(self.ALLOWED_EXTENSIONS.keys())
    
    def validate(
        self, 
        file_path: str, 
        check_content: bool = True
    ) -> ValidationReport:
        """
        Validate a file completely.
        
        Args:
            file_path: Path to the file
            check_content: Whether to check file content integrity
        
        Returns:
            ValidationReport with validation results
        """
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            return ValidationReport(
                is_valid=False,
                result=ValidationResult.FILE_NOT_FOUND,
                message=f"File not found: {file_path}",
                filename=path.name,
                file_size=0,
                file_extension=path.suffix.lower(),
            )
        
        # Get file info
        file_size = path.stat().st_size
        file_extension = path.suffix.lower()
        
        # Check extension
        if file_extension not in self.allowed_extensions:
            return ValidationReport(
                is_valid=False,
                result=ValidationResult.INVALID_EXTENSION,
                message=f"File extension '{file_extension}' is not allowed. "
                        f"Allowed: {', '.join(self.allowed_extensions)}",
                filename=path.name,
                file_size=file_size,
                file_extension=file_extension,
            )
        
        # Check file size
        if file_size > self.max_size:
            size_mb = file_size / (1024 * 1024)
            return ValidationReport(
                is_valid=False,
                result=ValidationResult.FILE_TOO_LARGE,
                message=f"File size ({size_mb:.2f}MB) exceeds maximum allowed size "
                        f"({self.max_size / (1024 * 1024):.0f}MB)",
                filename=path.name,
                file_size=file_size,
                file_extension=file_extension,
            )
        
        # Check if file is empty
        if file_size == 0:
            return ValidationReport(
                is_valid=False,
                result=ValidationResult.FILE_EMPTY,
                message="File is empty",
                filename=path.name,
                file_size=file_size,
                file_extension=file_extension,
            )
        
        # Check file content integrity if requested
        if check_content:
            content_check = self._check_file_integrity(path)
            if not content_check[0]:
                return ValidationReport(
                    is_valid=False,
                    result=ValidationResult.FILE_CORRUPTED,
                    message=content_check[1],
                    filename=path.name,
                    file_size=file_size,
                    file_extension=file_extension,
                )
        
        # Get MIME type
        mime_type = self.ALLOWED_EXTENSIONS.get(file_extension)
        
        return ValidationReport(
            is_valid=True,
            result=ValidationResult.VALID,
            message="File validation successful",
            filename=path.name,
            file_size=file_size,
            file_extension=file_extension,
            mime_type=mime_type,
        )
    
    def _check_file_integrity(self, path: Path) -> Tuple[bool, str]:
        """
        Check if file content matches expected format.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            ext = path.suffix.lower()
            
            # PDF files should start with %PDF
            if ext == '.pdf':
                with open(path, 'rb') as f:
                    header = f.read(8)
                    if not header.startswith(b'%PDF'):
                        return False, "Invalid PDF file header"
            
            # DOCX files are ZIP archives
            elif ext == '.docx' or ext == '.xlsx' or ext == '.pptx':
                import zipfile
                try:
                    with zipfile.ZipFile(path, 'r') as zf:
                        # Try to read first few bytes
                        zf.namelist()
                except zipfile.BadZipFile:
                    return False, f"Invalid {ext.upper()} file - corrupted ZIP structure"
            
            # Text-based files should be readable
            elif ext in ['.txt', '.csv', '.md', '.json', '.xml']:
                with open(path, 'r', encoding='utf-8') as f:
                    # Try to read first 1KB
                    f.read(1024)
            
            return True, ""
            
        except UnicodeDecodeError:
            return False, "File contains invalid character encoding"
        except Exception as e:
            return False, f"Error checking file integrity: {str(e)}"
    
    def get_supported_formats(self) -> dict:
        """Get dictionary of supported file formats."""
        return {
            ext.lstrip('.').upper(): mime 
            for ext, mime in self.ALLOWED_EXTENSIONS.items()
            if ext in self.allowed_extensions
        }
    
    def is_extension_supported(self, extension: str) -> bool:
        """Check if a file extension is supported."""
        return extension.lower() in self.allowed_extensions
    
    def get_max_size_mb(self) -> int:
        """Get maximum allowed file size in MB."""
        return self.max_size // (1024 * 1024)
