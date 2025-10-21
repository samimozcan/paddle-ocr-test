"""
Output Manager Module

Handles saving OCR results in various formats (JSON, text, etc.)
"""

import os
import json
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OutputManager:
    """
    Manages saving of OCR results to different output formats.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize output manager with configuration.
        
        Args:
            config: Dictionary containing output configuration
        """
        self.config = config
        output_config = config.get('output', {})
        self.output_dir = output_config.get('output_dir', 'output')
        self.save_json = output_config.get('save_json', True)
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save_results(self, results: Dict, filename_prefix: str) -> Dict[str, str]:
        """
        Save OCR results to files.
        
        Args:
            results: Dictionary containing OCR results
            filename_prefix: Prefix for output filenames
            
        Returns:
            Dictionary with paths to saved files
        """
        saved_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON format
        if self.save_json:
            json_path = os.path.join(
                self.output_dir,
                f"{filename_prefix}_{timestamp}.json"
            )
            self._save_json(results, json_path)
            saved_files['json'] = json_path
        
        # Save simple text format
        txt_path = os.path.join(
            self.output_dir,
            f"{filename_prefix}_{timestamp}.txt"
        )
        self._save_text(results, txt_path)
        saved_files['text'] = txt_path
        
        logger.info(f"Results saved to {self.output_dir}")
        return saved_files
    
    def _save_json(self, results: Dict, file_path: str):
        """
        Save results as JSON file.
        
        Args:
            results: Results dictionary
            file_path: Path to save the JSON file
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved JSON results to {file_path}")
    
    def _save_text(self, results: Dict, file_path: str):
        """
        Save results as a human-readable text file.
        
        Args:
            results: Results dictionary
            file_path: Path to save the text file
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("OCR RESULTS\n")
            f.write("=" * 60 + "\n\n")
            
            if 'pages' in results:
                # Multi-page results
                for page_num, page_data in enumerate(results['pages'], start=1):
                    f.write(f"\n--- Page {page_num} ---\n\n")
                    self._write_page_results(f, page_data)
            else:
                # Single page results
                self._write_page_results(f, results)
        
        logger.info(f"Saved text results to {file_path}")
    
    def _write_page_results(self, file, page_data: Dict):
        """
        Write page results to file.
        
        Args:
            file: File object to write to
            page_data: Dictionary containing page OCR results
        """
        if 'mapped_result' in page_data:
            mapped = page_data['mapped_result']
            file.write("Mapped Fields:\n")
            file.write("-" * 40 + "\n")
            
            for field_name, field_data in mapped['fields'].items():
                if field_data is not None:
                    text = field_data['text']
                    conf = field_data['confidence']
                    file.write(f"{field_name}: {text} (confidence: {conf:.2f})\n")
                else:
                    file.write(f"{field_name}: [Not detected]\n")
            
            file.write("\n")
            
            # Show metadata
            metadata = mapped.get('metadata', {})
            file.write(f"Metadata:\n")
            file.write(f"  - Mapping mode: {metadata.get('mapping_mode', 'N/A')}\n")
            file.write(f"  - Total boxes: {metadata.get('total_boxes', 0)}\n")
            file.write(f"  - Mapped fields: {metadata.get('mapped_fields', 0)}\n")
            
            unmapped = metadata.get('unmapped_boxes', [])
            if unmapped:
                file.write(f"\nUnmapped boxes ({len(unmapped)}):\n")
                for box in unmapped:
                    file.write(f"  - {box['text']} (confidence: {box.get('confidence', 0):.2f})\n")
        
        if 'raw_boxes' in page_data:
            file.write("\n\nAll Detected Text:\n")
            file.write("-" * 40 + "\n")
            for idx, box in enumerate(page_data['raw_boxes'], start=1):
                file.write(f"{idx}. {box['text']} (conf: {box['confidence']:.2f})\n")
