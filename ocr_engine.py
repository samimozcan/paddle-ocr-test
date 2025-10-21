"""
PaddleOCR Engine Module

This module provides the core OCR functionality using PaddlePaddle's OCR engine.
It handles text detection, recognition, and bounding box extraction from images.
"""

import os
from typing import List, Dict, Tuple, Optional
import numpy as np
from paddleocr import PaddleOCR
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCREngine:
    """
    Wrapper class for PaddleOCR with enhanced functionality.
    
    Handles initialization of the OCR engine and provides methods for
    text detection and recognition with bounding box information.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the OCR engine with configuration.
        
        Args:
            config: Dictionary containing OCR configuration parameters
        """
        self.config = config
        ocr_config = config.get('ocr', {})
        
        # Initialize PaddleOCR with configuration
        # Note: PaddleOCR will download models on first run
        logger.info("Initializing PaddleOCR engine...")
        
        # Determine device based on config
        use_gpu = ocr_config.get('use_gpu', False)
        device = 'gpu' if use_gpu else 'cpu'
        
        # Use simplified initialization to avoid segfaults on some systems
        # Disable doc analysis which can cause issues on macOS
        try:
            self.ocr = PaddleOCR(
                lang=ocr_config.get('lang', 'en'),
                device=device,
                use_angle_cls=False,  # Disable to avoid segfault
                det_db_thresh=ocr_config.get('det_db_thresh', 0.3),
                det_db_box_thresh=ocr_config.get('det_db_box_thresh', 0.6),
                rec_batch_num=ocr_config.get('rec_batch_num', 6)
            )
            logger.info("OCR engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            raise
    
    def process_image(self, image_path: str) -> List[Dict]:
        """
        Process an image and extract text with bounding boxes.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of dictionaries containing bounding box and text information
            Each dict has: 'box', 'text', 'confidence', 'position'
        """
        logger.info(f"Processing image: {image_path}")
        
        # Perform OCR on the image
        # Result format: [[[box], (text, confidence)], ...]
        # Note: cls parameter removed in newer PaddleOCR versions
        result = self.ocr.ocr(image_path)
        
        if not result or not result[0]:
            logger.warning(f"No text detected in {image_path}")
            return []
        
        # Parse and structure the results
        structured_results = []
        for idx, line in enumerate(result[0]):
            box = line[0]  # Bounding box coordinates [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            text = line[1][0]  # Recognized text
            confidence = line[1][1]  # Confidence score
            
            # Calculate center position for sorting
            # This helps in determining reading order
            center_x = sum([point[0] for point in box]) / 4
            center_y = sum([point[1] for point in box]) / 4
            
            structured_results.append({
                'box': box,
                'text': text,
                'confidence': confidence,
                'position': {
                    'center_x': center_x,
                    'center_y': center_y,
                    'min_x': min([point[0] for point in box]),
                    'min_y': min([point[1] for point in box]),
                    'max_x': max([point[0] for point in box]),
                    'max_y': max([point[1] for point in box])
                }
            })
        
        logger.info(f"Detected {len(structured_results)} text regions")
        return structured_results
    
    def sort_boxes_reading_order(self, boxes: List[Dict]) -> List[Dict]:
        """
        Sort bounding boxes in reading order (top to bottom, left to right).
        
        This is crucial for sequential field mapping where the order of detected
        text boxes corresponds to form fields in order.
        
        Args:
            boxes: List of box dictionaries with position information
            
        Returns:
            Sorted list of boxes in reading order
        """
        # Sort by y-coordinate first (top to bottom), then x-coordinate (left to right)
        # Group boxes that are on roughly the same line (within threshold)
        y_threshold = 20  # pixels - adjust based on typical text height
        
        # Sort primarily by y-coordinate
        sorted_boxes = sorted(boxes, key=lambda x: (
            x['position']['center_y'] // y_threshold,  # Group by approximate line
            x['position']['center_x']  # Then sort left to right
        ))
        
        return sorted_boxes
    
    def filter_boxes_by_confidence(self, boxes: List[Dict], min_confidence: float = 0.5) -> List[Dict]:
        """
        Filter out boxes with low confidence scores.
        
        Args:
            boxes: List of box dictionaries
            min_confidence: Minimum confidence threshold (0.0 to 1.0)
            
        Returns:
            Filtered list of boxes
        """
        filtered = [box for box in boxes if box['confidence'] >= min_confidence]
        logger.info(f"Filtered {len(boxes) - len(filtered)} low-confidence boxes")
        return filtered
