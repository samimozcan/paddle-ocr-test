#!/usr/bin/env python3
"""
PaddleOCR Application - Main Entry Point

Command-line application for processing PDFs and images with OCR,
extracting text with bounding boxes and mapping to structured fields.

Usage:
    python main.py <input_file> [options]

Example:
    python main.py document.pdf
    python main.py image.png --config custom_config.yaml
    python main.py form.pdf --no-viz --confidence 0.8
"""

import os
import sys
import argparse
import yaml
import logging
from typing import Dict, List
from colorama import init, Fore, Style

# Import local modules
from ocr_engine import OCREngine
from pdf_processor import PDFProcessor
from box_mapper import BoxMapper
from visualizer import Visualizer
from output_manager import OutputManager

# Initialize colorama for colored terminal output
init(autoreset=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OCRApplication:
    """
    Main application class that orchestrates the OCR process.
    
    Coordinates between PDF processing, OCR engine, box mapping,
    visualization, and output generation.
    """
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize the OCR application.
        
        Args:
            config_path: Path to configuration YAML file
        """
        self.config = self._load_config(config_path)
        
        # Initialize components
        logger.info("Initializing OCR application...")
        self.ocr_engine = OCREngine(self.config)
        self.pdf_processor = PDFProcessor(self.config)
        self.box_mapper = BoxMapper(self.config)
        self.visualizer = Visualizer(self.config)
        self.output_manager = OutputManager(self.config)
        
        logger.info("Application initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to config file
            
        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def process_file(self, file_path: str, min_confidence: float = 0.5, 
                    save_visualization: bool = True) -> Dict:
        """
        Process a PDF or image file with OCR.
        
        This is the main processing pipeline:
        1. Convert PDF to images (if needed)
        2. Run OCR on each image
        3. Sort and filter bounding boxes
        4. Map boxes to structured fields
        5. Generate visualizations
        6. Save results
        
        Args:
            file_path: Path to the input file (PDF or image)
            min_confidence: Minimum confidence threshold for text detection
            save_visualization: Whether to save visualization images
            
        Returns:
            Dictionary containing complete results
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Processing: {Fore.WHITE}{file_path}")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        # Check if input is PDF or image
        is_pdf = self.pdf_processor.is_pdf(file_path)
        temp_images = []
        
        try:
            if is_pdf:
                print(f"{Fore.YELLOW}📄 Converting PDF to images...")
                image_paths = self.pdf_processor.convert_pdf_to_images(file_path)
                temp_images = image_paths  # Track for cleanup
            else:
                image_paths = [file_path]
            
            # Process each page/image
            all_results = []
            for page_num, image_path in enumerate(image_paths, start=1):
                print(f"\n{Fore.GREEN}📝 Processing page {page_num}/{len(image_paths)}...")
                
                # Run OCR
                raw_boxes = self.ocr_engine.process_image(image_path)
                
                if not raw_boxes:
                    print(f"{Fore.RED}⚠️  No text detected on page {page_num}")
                    continue
                
                # Filter by confidence
                filtered_boxes = self.ocr_engine.filter_boxes_by_confidence(
                    raw_boxes, min_confidence
                )
                
                # Sort boxes in reading order
                sorted_boxes = self.ocr_engine.sort_boxes_reading_order(filtered_boxes)
                
                print(f"{Fore.GREEN}✓ Detected {len(sorted_boxes)} text regions")
                
                # Map boxes to fields
                width, height = self.pdf_processor.get_image_dimensions(image_path)
                mapped_result = self.box_mapper.map_boxes_to_fields(
                    sorted_boxes, width, height
                )
                
                print(f"{Fore.GREEN}✓ Mapped {mapped_result['metadata']['mapped_fields']} fields")
                
                # Create visualization if requested
                viz_path = None
                field_viz_path = None
                if save_visualization:
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    output_dir = self.config.get('output', {}).get('output_dir', 'output')
                    
                    viz_path = os.path.join(
                        output_dir,
                        f"{base_name}_page_{page_num}_boxes.png"
                    )
                    field_viz_path = os.path.join(
                        output_dir,
                        f"{base_name}_page_{page_num}_fields.png"
                    )
                    
                    print(f"{Fore.YELLOW}🎨 Creating visualizations...")
                    self.visualizer.draw_boxes(image_path, sorted_boxes, viz_path)
                    self.visualizer.create_field_visualization(
                        image_path, mapped_result, field_viz_path
                    )
                
                # Collect results for this page
                page_result = {
                    'page_number': page_num,
                    'image_path': image_path,
                    'raw_boxes': raw_boxes,
                    'filtered_boxes': filtered_boxes,
                    'mapped_result': mapped_result,
                    'visualization_path': viz_path,
                    'field_visualization_path': field_viz_path
                }
                all_results.append(page_result)
            
            # Compile final results
            final_result = {
                'input_file': file_path,
                'is_pdf': is_pdf,
                'total_pages': len(image_paths),
                'pages': all_results,
                'config': {
                    'min_confidence': min_confidence,
                    'mapping_mode': self.config.get('box_mapping', {}).get('mode', 'sequential')
                }
            }
            
            # Save results
            print(f"\n{Fore.YELLOW}💾 Saving results...")
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            saved_files = self.output_manager.save_results(final_result, base_name)
            
            # Print summary
            self._print_summary(final_result, saved_files)
            
            return final_result
            
        finally:
            # Cleanup temporary images
            if temp_images and is_pdf:
                logger.info("Cleaning up temporary images...")
                self.pdf_processor.cleanup_temp_images(temp_images)
    
    def _print_summary(self, results: Dict, saved_files: Dict):
        """
        Print a summary of the OCR results.
        
        Args:
            results: Complete results dictionary
            saved_files: Dictionary of saved file paths
        """
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}RESULTS SUMMARY")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        for page in results['pages']:
            page_num = page['page_number']
            mapped = page['mapped_result']
            
            print(f"{Fore.GREEN}Page {page_num}:")
            print(f"{Fore.WHITE}  Detected boxes: {mapped['metadata']['total_boxes']}")
            print(f"{Fore.WHITE}  Mapped fields: {mapped['metadata']['mapped_fields']}")
            print(f"\n{Fore.YELLOW}  Extracted Data:")
            
            simple_data = self.box_mapper.create_simple_output(mapped)
            for field_name, value in simple_data.items():
                if value:
                    print(f"{Fore.WHITE}    {field_name}: {Fore.GREEN}{value}")
                else:
                    print(f"{Fore.WHITE}    {field_name}: {Fore.RED}[Not detected]")
            print()
        
        print(f"{Fore.CYAN}Output files:")
        for file_type, file_path in saved_files.items():
            print(f"{Fore.WHITE}  {file_type}: {Fore.GREEN}{file_path}")
        
        print(f"\n{Fore.GREEN}✓ Processing complete!\n")


def main():
    """
    Main entry point for the application.
    """
    parser = argparse.ArgumentParser(
        description='PaddleOCR Application - Extract text from PDFs and images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py document.pdf
  python main.py image.png --config custom_config.yaml
  python main.py form.pdf --no-viz --confidence 0.8
  python main.py invoice.pdf --log-level DEBUG
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Path to input file (PDF or image)'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--confidence',
        type=float,
        default=0.5,
        help='Minimum confidence threshold for text detection (0.0-1.0, default: 0.5)'
    )
    
    parser.add_argument(
        '--no-viz',
        action='store_true',
        help='Disable visualization output'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        # Initialize and run application
        app = OCRApplication(args.config)
        app.process_file(
            args.input_file,
            min_confidence=args.confidence,
            save_visualization=not args.no_viz
        )
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {str(e)}")
        logger.exception("Application error")
        sys.exit(1)


if __name__ == '__main__':
    main()
