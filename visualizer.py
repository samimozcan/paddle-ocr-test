"""
Visualization Module

Provides utilities to visualize OCR results with bounding boxes.
"""

import os
from typing import List, Dict, Tuple
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)


class Visualizer:
    """
    Visualizes OCR results by drawing bounding boxes on images.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize visualizer with configuration.
        
        Args:
            config: Dictionary containing visualization configuration
        """
        self.config = config
        output_config = config.get('output', {})
        self.color = tuple(output_config.get('visualization_color', [0, 255, 0]))
        self.thickness = 2
    
    def draw_boxes(self, image_path: str, boxes: List[Dict], 
                   output_path: str, show_text: bool = True) -> str:
        """
        Draw bounding boxes on an image and save the result.
        
        Args:
            image_path: Path to the original image
            boxes: List of box dictionaries with 'box' and 'text' keys
            output_path: Path to save the annotated image
            show_text: Whether to display the recognized text above boxes
            
        Returns:
            Path to the saved visualization
        """
        # Read image using OpenCV
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        # Draw each bounding box
        for idx, box_info in enumerate(boxes):
            box = box_info['box']
            text = box_info['text']
            confidence = box_info.get('confidence', 0)
            
            # Convert box coordinates to integers
            # Box format: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            points = np.array(box, dtype=np.int32)
            
            # Draw the bounding box polygon
            cv2.polylines(image, [points], isClosed=True, 
                         color=self.color, thickness=self.thickness)
            
            # Optionally add text label
            if show_text and text:
                # Position text above the top-left corner of the box
                text_x = int(points[0][0])
                text_y = int(points[0][1]) - 10
                
                # Add background rectangle for better readability
                label = f"{text} ({confidence:.2f})"
                (text_width, text_height), _ = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                )
                
                cv2.rectangle(
                    image,
                    (text_x, text_y - text_height - 5),
                    (text_x + text_width, text_y + 5),
                    self.color,
                    -1  # Filled rectangle
                )
                
                # Draw text
                cv2.putText(
                    image,
                    label,
                    (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),  # Black text
                    1,
                    cv2.LINE_AA
                )
        
        # Save the annotated image
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, image)
        logger.info(f"Saved visualization to {output_path}")
        
        return output_path
    
    def create_field_visualization(self, image_path: str, mapped_result: Dict,
                                   output_path: str) -> str:
        """
        Create visualization with field labels instead of recognized text.
        
        This shows which box corresponds to which field (e.g., firstName, lastName).
        Useful for debugging and understanding the mapping.
        
        Args:
            image_path: Path to the original image
            mapped_result: Result from BoxMapper with field assignments
            output_path: Path to save the visualization
            
        Returns:
            Path to the saved visualization
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        # Define colors for different fields (cycling through a palette)
        colors = [
            (0, 255, 0),    # Green
            (255, 0, 0),    # Blue
            (0, 0, 255),    # Red
            (255, 255, 0),  # Cyan
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Yellow
        ]
        
        # Draw boxes for each mapped field
        for idx, (field_name, field_data) in enumerate(mapped_result['fields'].items()):
            if field_data is not None:
                box = field_data['box']
                color = colors[idx % len(colors)]
                
                points = np.array(box, dtype=np.int32)
                cv2.polylines(image, [points], isClosed=True, 
                             color=color, thickness=self.thickness)
                
                # Add field name label
                text_x = int(points[0][0])
                text_y = int(points[0][1]) - 10
                
                cv2.putText(
                    image,
                    field_name,
                    (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2,
                    cv2.LINE_AA
                )
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, image)
        logger.info(f"Saved field visualization to {output_path}")
        
        return output_path
