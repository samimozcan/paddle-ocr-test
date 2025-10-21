"""
Box Mapping Module

This module handles mapping of detected bounding boxes to structured fields.
Supports sequential and positional mapping strategies.
"""

from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BoxMapper:
    """
    Maps detected text boxes to structured field names.
    
    Supports multiple mapping strategies:
    - Sequential: Assigns boxes in reading order to a predefined list of fields
    - Positional: Assigns boxes based on their position on the page
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the box mapper with configuration.
        
        Args:
            config: Dictionary containing box mapping configuration
        """
        self.config = config
        self.mapping_config = config.get('box_mapping', {})
        self.mode = self.mapping_config.get('mode', 'sequential')
        logger.info(f"BoxMapper initialized with mode: {self.mode}")
    
    def map_boxes_to_fields(self, boxes: List[Dict], image_width: Optional[int] = None, 
                           image_height: Optional[int] = None) -> Dict[str, any]:
        """
        Map detected boxes to structured fields based on the configured mode.
        
        Args:
            boxes: List of detected boxes (should be sorted in reading order for sequential mode)
            image_width: Width of the image (required for positional mode)
            image_height: Height of the image (required for positional mode)
            
        Returns:
            Dictionary mapping field names to detected text values
        """
        if self.mode == 'sequential':
            return self._map_sequential(boxes)
        elif self.mode == 'positional':
            if image_width is None or image_height is None:
                raise ValueError("Image dimensions required for positional mapping")
            return self._map_positional(boxes, image_width, image_height)
        else:
            logger.warning(f"Unknown mapping mode: {self.mode}, falling back to sequential")
            return self._map_sequential(boxes)
    
    def _map_sequential(self, boxes: List[Dict]) -> Dict[str, any]:
        """
        Map boxes sequentially based on reading order.
        
        The first detected box maps to the first field, second box to second field, etc.
        This is useful for forms where fields appear in a predictable order.
        
        Args:
            boxes: List of boxes in reading order
            
        Returns:
            Dictionary with field names as keys and detected text as values
        """
        fields = self.mapping_config.get('sequential_fields', [])
        result = {
            'fields': {},
            'metadata': {
                'mapping_mode': 'sequential',
                'total_boxes': len(boxes),
                'mapped_fields': 0,
                'unmapped_boxes': []
            }
        }
        
        # Map boxes to fields based on position in the list
        for idx, box in enumerate(boxes):
            if idx < len(fields):
                field_name = fields[idx]
                result['fields'][field_name] = {
                    'text': box['text'],
                    'confidence': box['confidence'],
                    'box': box['box']
                }
                result['metadata']['mapped_fields'] += 1
            else:
                # Extra boxes that don't have a corresponding field
                result['metadata']['unmapped_boxes'].append({
                    'index': idx,
                    'text': box['text'],
                    'confidence': box['confidence']
                })
        
        # Add any fields that weren't filled (not enough boxes detected)
        for field in fields[len(boxes):]:
            result['fields'][field] = None
        
        logger.info(f"Sequential mapping: {result['metadata']['mapped_fields']} fields mapped")
        return result
    
    def _map_positional(self, boxes: List[Dict], image_width: int, 
                       image_height: int) -> Dict[str, any]:
        """
        Map boxes based on their position in the image.
        
        Uses predefined regions to determine which field each box belongs to.
        Regions are defined as percentages of image dimensions.
        
        Args:
            boxes: List of detected boxes
            image_width: Width of the image
            image_height: Height of the image
            
        Returns:
            Dictionary with field names and detected text
        """
        positional_map = self.mapping_config.get('positional_mapping', {})
        result = {
            'fields': {},
            'metadata': {
                'mapping_mode': 'positional',
                'total_boxes': len(boxes),
                'mapped_fields': 0,
                'unmapped_boxes': []
            }
        }
        
        # Initialize all fields as None
        for field_name in positional_map.keys():
            result['fields'][field_name] = None
        
        # Map each box to a field based on its position
        for box_idx, box in enumerate(boxes):
            center_x = box['position']['center_x']
            center_y = box['position']['center_y']
            
            # Normalize coordinates to percentages
            norm_x = center_x / image_width
            norm_y = center_y / image_height
            
            # Check which region this box falls into
            matched_field = None
            for field_name, field_config in positional_map.items():
                region = field_config.get('region', [])
                if len(region) == 4:
                    x_min, y_min, x_max, y_max = region
                    if x_min <= norm_x <= x_max and y_min <= norm_y <= y_max:
                        matched_field = field_name
                        break
            
            if matched_field:
                # If multiple boxes match the same field, keep the one with higher confidence
                if result['fields'][matched_field] is None or \
                   box['confidence'] > result['fields'][matched_field]['confidence']:
                    result['fields'][matched_field] = {
                        'text': box['text'],
                        'confidence': box['confidence'],
                        'box': box['box']
                    }
                    result['metadata']['mapped_fields'] += 1
            else:
                result['metadata']['unmapped_boxes'].append({
                    'index': box_idx,
                    'text': box['text'],
                    'confidence': box['confidence']
                })
        
        logger.info(f"Positional mapping: {result['metadata']['mapped_fields']} fields mapped")
        return result
    
    def create_simple_output(self, mapped_result: Dict) -> Dict[str, str]:
        """
        Create a simplified output with just field names and text values.
        
        Args:
            mapped_result: Full mapping result with metadata
            
        Returns:
            Simple dictionary with field names and text values
        """
        simple = {}
        for field_name, field_data in mapped_result['fields'].items():
            if field_data is not None:
                simple[field_name] = field_data['text']
            else:
                simple[field_name] = None
        return simple
