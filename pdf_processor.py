"""
PDF Processor Module

Handles conversion of PDF files to images for OCR processing.
Supports processing single or multiple pages.
"""

import os
from typing import List, Optional, Tuple, Dict
from PIL import Image
import logging
try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Converts PDF files to images for OCR processing.
    
    Uses pdf2image library which requires poppler-utils to be installed on the system.
    On macOS: brew install poppler
    On Ubuntu/Debian: apt-get install poppler-utils
    On Windows: Download poppler binaries
    """
    
    def __init__(self, config: Dict):
        """
        Initialize PDF processor with configuration.
        
        Args:
            config: Dictionary containing PDF processing configuration
        """
        self.config = config
        self.pdf_config = config.get('pdf', {})
        self.dpi = self.pdf_config.get('dpi', 300)
        self.first_page = self.pdf_config.get('first_page')
        self.last_page = self.pdf_config.get('last_page')
        
        if convert_from_path is None:
            logger.warning("pdf2image not installed. PDF processing may not work.")
    
    def is_pdf(self, file_path: str) -> bool:
        """
        Check if the file is a PDF.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is a PDF, False otherwise
        """
        return file_path.lower().endswith('.pdf')
    
    def convert_pdf_to_images(self, pdf_path: str, output_dir: Optional[str] = None) -> List[str]:
        """
        Convert PDF file to images.
        
        Each page of the PDF is converted to a separate image file.
        Images are saved to the output directory with sequential naming.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save converted images (optional)
            
        Returns:
            List of paths to the generated image files
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if convert_from_path is None:
            raise ImportError("pdf2image is not installed. Install with: pip install pdf2image")
        
        logger.info(f"Converting PDF to images: {pdf_path}")
        
        # Create output directory if needed
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(pdf_path), 'temp_images')
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert PDF to images
        # This may take a while for large PDFs
        try:
            images = convert_from_path(
                pdf_path,
                dpi=self.dpi,
                first_page=self.first_page,
                last_page=self.last_page
            )
        except Exception as e:
            logger.error(f"Failed to convert PDF: {e}")
            raise
        
        # Save images and collect paths
        image_paths = []
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        for i, image in enumerate(images, start=1):
            image_path = os.path.join(output_dir, f"{base_name}_page_{i}.png")
            image.save(image_path, 'PNG')
            image_paths.append(image_path)
            logger.info(f"Saved page {i} to {image_path}")
        
        logger.info(f"Converted {len(image_paths)} pages from PDF")
        return image_paths
    
    def get_image_dimensions(self, image_path: str) -> Tuple[int, int]:
        """
        Get the dimensions of an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (width, height)
        """
        with Image.open(image_path) as img:
            return img.size
    
    def cleanup_temp_images(self, image_paths: List[str]):
        """
        Remove temporary image files created during PDF processing.
        
        Args:
            image_paths: List of image file paths to remove
        """
        for image_path in image_paths:
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
                    logger.debug(f"Removed temporary image: {image_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary image {image_path}: {e}")
