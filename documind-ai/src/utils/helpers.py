"""
DocuMind AI - Helper Functions
Common utility functions used throughout the application.
"""

import uuid
import re
import os
from datetime import datetime
from typing import Optional
from pathlib import Path


def generate_unique_id(prefix: str = "") -> str:
    """
    Generate a unique identifier.
    
    Args:
        prefix: Optional prefix to add to the ID
        
    Returns:
        Unique ID string (e.g., "doc_550e8400-e29b-41d4-a716-446655440000")
    """
    unique_id = str(uuid.uuid4())
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB", "256 KB")
    """
    if size_bytes < 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.2f} {units[unit_index]}"


def clean_filename(filename: str, max_length: int = 100) -> str:
    """
    Clean and sanitize a filename for safe storage.
    
    Args:
        filename: Original filename
        max_length: Maximum length of filename
        
    Returns:
        Sanitized filename
    """
    # Remove path separators
    filename = os.path.basename(filename)
    
    # Convert to lowercase
    filename = filename.lower()
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove special characters (keep only alphanumeric, dots, underscores, hyphens)
    filename = re.sub(r'[^a-z0-9._-]', '', filename)
    
    # Remove multiple consecutive dots
    filename = re.sub(r'\.{2,}', '.', filename)
    
    # Trim to max length (preserving extension)
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        max_name_length = max_length - len(ext)
        filename = name[:max_name_length] + ext
    
    # Ensure filename is not empty
    if not filename or filename == '.':
        filename = f"unnamed_{generate_unique_id()}"
    
    return filename


def get_current_timestamp(format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Get current timestamp as formatted string.
    
    Args:
        format_string: strftime format string
        
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime(format_string)


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    # Ensure suffix fits
    if len(suffix) >= max_length:
        return text[:max_length]
    
    return text[:max_length - len(suffix)] + suffix


def parse_date(date_string: str) -> Optional[datetime]:
    """
    Parse date from various formats.
    
    Args:
        date_string: Date string in various formats
        
    Returns:
        datetime object or None if parsing fails
    """
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%m/%d/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    return None


def extract_email_addresses(text: str) -> list:
    """
    Extract email addresses from text.
    
    Args:
        text: Text to search
        
    Returns:
        List of email addresses found
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def extract_phone_numbers(text: str) -> list:
    """
    Extract phone numbers from text (various formats).
    
    Args:
        text: Text to search
        
    Returns:
        List of phone numbers found
    """
    # Matches various phone number formats
    phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
    return re.findall(phone_pattern, text)


def ensure_directory(path: str) -> Path:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_file_extension(filename: str) -> str:
    """
    Get file extension in lowercase without dot.
    
    Args:
        filename: Filename with extension
        
    Returns:
        Extension without dot (e.g., "pdf", "docx")
    """
    return Path(filename).suffix.lower().lstrip('.')


def calculate_read_time(text: str, words_per_minute: int = 200) -> int:
    """
    Calculate estimated reading time in minutes.
    
    Args:
        text: Text content
        words_per_minute: Reading speed (default 200 wpm)
        
    Returns:
        Estimated minutes to read
    """
    word_count = len(text.split())
    return max(1, round(word_count / words_per_minute))


def mask_sensitive_data(data: str, data_type: str = "email") -> str:
    """
    Mask sensitive data for display.
    
    Args:
        data: Sensitive data to mask
        data_type: Type of data ("email", "phone", "ssn")
        
    Returns:
        Masked string
    """
    if data_type == "email":
        if '@' not in data:
            return "***"
        username, domain = data.split('@', 1)
        masked_username = username[0] + "***" + username[-1] if len(username) > 1 else "***"
        return f"{masked_username}@{domain}"
    
    elif data_type == "phone":
        digits = re.sub(r'\D', '', data)
        if len(digits) >= 4:
            return "***-***-" + digits[-4:]
        return "***-***-****"
    
    elif data_type == "ssn":
        digits = re.sub(r'\D', '', data)
        if len(digits) >= 4:
            return "***-**-" + digits[-4:]
        return "***-**-****"
    
    return "***"
