"""
OCR Processor Module
Extract text from scanned PDFs and images using Tesseract OCR
"""

from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class OCRProcessor:
    """
    Extract text from scanned documents and images
    
    Supports:
    - Scanned PDFs (no selectable text)
    - Image files (JPG, PNG, TIFF, BMP)
    - Mixed PDFs (some pages scanned, some text-based)
    
    Backends:
    - Tesseract OCR (local, free)
    - AWS Textract (cloud, paid, higher accuracy)
    - Google Cloud Vision (cloud, paid)
    """
    
    def __init__(
        self,
        backend: str = "tesseract",
        language: str = "eng",
        psm_mode: int = 3,
        oem_mode: int = 3
    ):
        """
        Initialize OCR processor
        
        Args:
            backend: OCR backend to use ("tesseract", "textract", "vision")
            language: Language code for OCR (e.g., "eng", "spa", "fra")
            psm_mode: Page segmentation mode (0-14)
            oem_mode: OCR Engine mode (0-3)
        """
        self.backend = backend
        self.language = language
        self.psm_mode = psm_mode
        self.oem_mode = oem_mode
        
        self._initialized = False
        self._api = None
        
    def _initialize(self):
        """Initialize the OCR backend"""
        if self._initialized:
            return
            
        if self.backend == "tesseract":
            try:
                import pytesseract
                from PIL import Image
                
                # Test tesseract installation
                pytesseract.get_tesseract_version()
                self._api = pytesseract
                self._initialized = True
                logger.info("Tesseract OCR initialized successfully")
                
            except ImportError:
                logger.error("pytesseract not installed. Run: pip install pytesseract pillow")
                raise
            except Exception as e:
                logger.error(f"Tesseract initialization failed: {e}")
                raise
                
        elif self.backend == "textract":
            try:
                import boto3
                
                self._client = boto3.client('textract')
                self._initialized = True
                logger.info("AWS Textract initialized successfully")
                
            except ImportError:
                logger.error("boto3 not installed. Run: pip install boto3")
                raise
            except Exception as e:
                logger.error(f"Textract initialization failed: {e}")
                raise
                
        elif self.backend == "vision":
            try:
                from google.cloud import vision
                
                self._client = vision.ImageAnnotatorClient()
                self._initialized = True
                logger.info("Google Cloud Vision initialized successfully")
                
            except ImportError:
                logger.error("google-cloud-vision not installed. Run: pip install google-cloud-vision")
                raise
            except Exception as e:
                logger.error(f"Vision initialization failed: {e}")
                raise
        else:
            raise ValueError(f"Unknown OCR backend: {self.backend}")
    
    def process_image(
        self,
        image_path: Union[str, Path],
        dpi: int = 300
    ) -> Dict[str, Any]:
        """
        Extract text from an image file
        
        Args:
            image_path: Path to image file
            dpi: DPI for processing (higher = better quality, slower)
            
        Returns:
            Dictionary with extracted text and metadata
        """
        self._initialize()
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
            
        logger.info(f"Processing image with OCR: {image_path}")
        
        if self.backend == "tesseract":
            return self._process_with_tesseract(image_path)
        elif self.backend == "textract":
            return self._process_with_textract(image_path)
        elif self.backend == "vision":
            return self._process_with_vision(image_path)
        else:
            raise ValueError(f"Unknown backend: {self.backend}")
    
    def _process_with_tesseract(self, image_path: Path) -> Dict[str, Any]:
        """Process image using Tesseract"""
        from PIL import Image
        
        # Open image
        img = Image.open(image_path)
        
        # Configure OCR
        custom_config = f'--oem {self.oem_mode} --psm {self.psm_mode} -l {self.language}'
        
        # Extract text
        text = self._api.image_to_string(img, config=custom_config)
        
        # Get detailed data including confidence scores
        data = self._api.image_to_data(img, config=custom_config, output_type=self._api.Output.DICT)
        
        # Calculate average confidence
        confidences = [c for c in data['conf'] if c != -1]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            'text': text.strip(),
            'confidence': avg_confidence,
            'language': self.language,
            'backend': 'tesseract',
            'source': str(image_path),
            'pages': 1
        }
    
    def _process_with_textract(self, image_path: Path) -> Dict[str, Any]:
        """Process image using AWS Textract"""
        # Read image bytes
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        # Call Textract
        response = self._client.detect_document_text(Document={'Bytes': image_bytes})
        
        # Extract text from blocks
        lines = []
        confidence_sum = 0
        confidence_count = 0
        
        for block in response['Blocks']:
            if block['BlockType'] == 'LINE':
                lines.append(block['Text'])
                confidence_sum += block['Confidence']
                confidence_count += 1
        
        text = '\n'.join(lines)
        avg_confidence = confidence_sum / confidence_count if confidence_count > 0 else 0
        
        return {
            'text': text.strip(),
            'confidence': avg_confidence,
            'language': 'en',  # Textract auto-detects
            'backend': 'textract',
            'source': str(image_path),
            'pages': 1
        }
    
    def _process_with_vision(self, image_path: Path) -> Dict[str, Any]:
        """Process image using Google Cloud Vision"""
        from google.cloud import vision
        
        # Read image
        with open(image_path, 'rb') as f:
            content = f.read()
        
        image = vision.Image(content=content)
        
        # Perform text detection
        response = self._client.text_detection(image=image)
        texts = response.text_annotations
        
        if not texts:
            return {
                'text': '',
                'confidence': 0,
                'language': 'unknown',
                'backend': 'vision',
                'source': str(image_path),
                'pages': 1
            }
        
        # First annotation contains full text
        full_text = texts[0].description
        
        # Calculate average confidence (Vision doesn't provide per-word confidence in text_detection)
        avg_confidence = 100.0  # Assume high confidence if text was detected
        
        return {
            'text': full_text.strip(),
            'confidence': avg_confidence,
            'language': texts[0].locale if hasattr(texts[0], 'locale') else 'en',
            'backend': 'vision',
            'source': str(image_path),
            'pages': 1
        }
    
    def process_pdf(
        self,
        pdf_path: Union[str, Path],
        pages: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Process a PDF with OCR (for scanned PDFs)
        
        Args:
            pdf_path: Path to PDF file
            pages: List of page numbers to process (None = all pages)
            
        Returns:
            Dictionary with extracted text and metadata
        """
        self._initialize()
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        logger.info(f"Processing PDF with OCR: {pdf_path}")
        
        try:
            from pdf2image import convert_from_path
        except ImportError:
            logger.error("pdf2image not installed. Run: pip install pdf2image")
            raise
        
        # Convert PDF pages to images
        images = convert_from_path(pdf_path, dpi=300)
        
        if pages:
            images = [images[i-1] for i in pages if i-1 < len(images)]
        
        # Process each page
        page_results = []
        all_text = []
        total_confidence = 0
        
        for i, img in enumerate(images):
            # Save temp image
            temp_path = pdf_path.parent / f".temp_page_{i}.png"
            img.save(temp_path, 'PNG')
            
            # OCR the page
            result = self.process_image(temp_path)
            
            page_results.append({
                'page_number': i + 1,
                'text': result['text'],
                'confidence': result['confidence']
            })
            
            all_text.append(result['text'])
            total_confidence += result['confidence']
            
            # Clean up temp file
            temp_path.unlink()
        
        return {
            'text': '\n\n'.join(all_text),
            'confidence': total_confidence / len(page_results) if page_results else 0,
            'language': self.language,
            'backend': self.backend,
            'source': str(pdf_path),
            'pages': len(page_results),
            'page_details': page_results
        }
    
    def is_scanned_pdf(self, pdf_path: Union[str, Path]) -> bool:
        """
        Check if a PDF is scanned (has no selectable text)
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            True if PDF appears to be scanned
        """
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                
                # Check first few pages for text
                text_found = False
                for i, page in enumerate(reader.pages[:3]):
                    text = page.extract_text()
                    if text and len(text.strip()) > 50:
                        text_found = True
                        break
                
                return not text_found
                
        except Exception as e:
            logger.warning(f"Error checking if PDF is scanned: {e}")
            return True  # Assume scanned if we can't check


def needs_ocr(pdf_path: Union[str, Path]) -> bool:
    """Check if a PDF needs OCR processing"""
    processor = OCRProcessor()
    return processor.is_scanned_pdf(pdf_path)
