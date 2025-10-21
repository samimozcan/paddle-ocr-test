"""
Example Usage Script

This script demonstrates how to use the PaddleOCR application
programmatically instead of via command line.
"""

from main import OCRApplication
from box_mapper import BoxMapper
import json

def example_basic_usage():
    """Basic usage example"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 60)
    
    # Initialize the application
    app = OCRApplication('config.yaml')
    
    # Process a file
    # Replace 'document.pdf' with your actual file
    results = app.process_file(
        file_path='document.pdf',
        min_confidence=0.5,
        save_visualization=True
    )
    
    # Access results
    print(f"\nProcessed {results['total_pages']} page(s)")
    
    for page in results['pages']:
        page_num = page['page_number']
        mapped_result = page['mapped_result']
        
        print(f"\nPage {page_num}:")
        print(f"  Detected boxes: {mapped_result['metadata']['total_boxes']}")
        print(f"  Mapped fields: {mapped_result['metadata']['mapped_fields']}")
        
        # Get simple field values
        simple_data = app.box_mapper.create_simple_output(mapped_result)
        print("\n  Extracted data:")
        for field, value in simple_data.items():
            print(f"    {field}: {value}")


def example_custom_processing():
    """Example with custom processing logic"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Custom Processing")
    print("=" * 60)
    
    # Initialize with custom config
    app = OCRApplication('config.yaml')
    
    # Process with custom settings
    results = app.process_file(
        file_path='form.pdf',
        min_confidence=0.7,  # Higher confidence threshold
        save_visualization=False  # Skip visualizations for speed
    )
    
    # Custom post-processing
    for page in results['pages']:
        # Filter unmapped boxes
        unmapped = page['mapped_result']['metadata'].get('unmapped_boxes', [])
        
        if unmapped:
            print(f"\nPage {page['page_number']} has {len(unmapped)} unmapped boxes:")
            for box in unmapped:
                print(f"  - {box['text']} (confidence: {box['confidence']:.2f})")


def example_batch_processing():
    """Example of processing multiple files"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Batch Processing")
    print("=" * 60)
    
    import os
    from glob import glob
    
    # Initialize once
    app = OCRApplication('config.yaml')
    
    # Find all PDFs in a directory
    pdf_files = glob('input_documents/*.pdf')
    
    all_results = []
    for pdf_file in pdf_files:
        print(f"\nProcessing {pdf_file}...")
        try:
            results = app.process_file(
                pdf_file,
                min_confidence=0.5,
                save_visualization=False
            )
            all_results.append({
                'file': pdf_file,
                'success': True,
                'results': results
            })
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
            all_results.append({
                'file': pdf_file,
                'success': False,
                'error': str(e)
            })
    
    # Summary
    successful = sum(1 for r in all_results if r['success'])
    print(f"\n\nBatch Summary:")
    print(f"  Total files: {len(pdf_files)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {len(pdf_files) - successful}")


def example_field_validation():
    """Example with custom field validation"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Field Validation")
    print("=" * 60)
    
    app = OCRApplication('config.yaml')
    results = app.process_file('form.pdf')
    
    # Validation rules
    def validate_email(email):
        """Simple email validation"""
        return '@' in email if email else False
    
    def validate_phone(phone):
        """Simple phone validation"""
        if not phone:
            return False
        # Remove common separators
        digits = ''.join(c for c in phone if c.isdigit())
        return len(digits) >= 10
    
    # Validate extracted fields
    for page in results['pages']:
        simple_data = app.box_mapper.create_simple_output(page['mapped_result'])
        
        print(f"\nPage {page['page_number']} validation:")
        
        if 'email' in simple_data:
            is_valid = validate_email(simple_data['email'])
            status = "✓" if is_valid else "✗"
            print(f"  {status} Email: {simple_data['email']}")
        
        if 'phone' in simple_data:
            is_valid = validate_phone(simple_data['phone'])
            status = "✓" if is_valid else "✗"
            print(f"  {status} Phone: {simple_data['phone']}")


def example_export_to_database():
    """Example of exporting results to a database structure"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Database Export")
    print("=" * 60)
    
    app = OCRApplication('config.yaml')
    results = app.process_file('form.pdf')
    
    # Convert to database-ready format
    database_records = []
    
    for page in results['pages']:
        simple_data = app.box_mapper.create_simple_output(page['mapped_result'])
        
        # Create a record
        record = {
            'document_id': results['input_file'],
            'page_number': page['page_number'],
            'extracted_at': None,  # Add timestamp
            'fields': simple_data,
            'confidence_avg': sum(
                box['confidence'] 
                for box in page['filtered_boxes']
            ) / len(page['filtered_boxes']) if page['filtered_boxes'] else 0
        }
        
        database_records.append(record)
    
    # Display what would be inserted
    print("\nDatabase records prepared:")
    print(json.dumps(database_records, indent=2))
    
    # In a real application, you would insert into database:
    # db.insert_many(database_records)


if __name__ == '__main__':
    print("\nPaddleOCR Application - Usage Examples\n")
    print("Note: These examples require actual input files.")
    print("Replace the file paths with your own documents.\n")
    
    # Uncomment the examples you want to run:
    
    # example_basic_usage()
    # example_custom_processing()
    # example_batch_processing()
    # example_field_validation()
    # example_export_to_database()
    
    print("\nTo run an example, uncomment it in the __main__ section.")
