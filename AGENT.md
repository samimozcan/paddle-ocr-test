# AGENT.md - Development Documentation

## 🏗️ Architecture Overview

This document provides detailed technical information about the PaddleOCR application architecture, design decisions, and implementation details for developers and AI agents working on this codebase.

## 📐 System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                    Main Application                      │
│                     (main.py)                           │
│  - CLI Interface                                        │
│  - Orchestration & Coordination                         │
└──────────────┬──────────────────────────────────────────┘
               │
               ├──────────────┬──────────────┬─────────────┬──────────────┐
               │              │              │             │              │
               ▼              ▼              ▼             ▼              ▼
       ┌──────────────┐ ┌──────────┐ ┌────────────┐ ┌──────────┐ ┌───────────┐
       │ OCR Engine   │ │   PDF    │ │    Box     │ │Visualizer│ │  Output   │
       │              │ │Processor │ │   Mapper   │ │          │ │  Manager  │
       │ ocr_engine.py│ │pdf_proc..│ │box_mapper..│ │visual... │ │output_... │
       └──────────────┘ └──────────┘ └────────────┘ └──────────┘ └───────────┘
               │              │              │             │              │
               └──────────────┴──────────────┴─────────────┴──────────────┘
                                          │
                                          ▼
                                  ┌──────────────┐
                                  │   Config     │
                                  │ (config.yaml)│
                                  └──────────────┘
```

### Component Responsibilities

#### 1. **main.py** - Application Orchestrator
- **Purpose**: Entry point and coordination layer
- **Responsibilities**:
  - CLI argument parsing
  - Component initialization
  - Process flow orchestration
  - Error handling and user feedback
  - Results compilation

**Key Design Decision**: Single entry point simplifies deployment and usage.

#### 2. **ocr_engine.py** - OCR Core
- **Purpose**: Interface to PaddleOCR functionality
- **Responsibilities**:
  - PaddleOCR initialization and configuration
  - Text detection and recognition
  - Bounding box extraction
  - Box sorting (reading order)
  - Confidence filtering

**Complex Sections**:

```python
def sort_boxes_reading_order(self, boxes: List[Dict]) -> List[Dict]:
    """
    Sorting algorithm explanation:
    
    1. Group boxes by approximate y-coordinate (vertical position)
       - Uses integer division by y_threshold to create "line groups"
       - Boxes within y_threshold pixels are considered on same line
    
    2. Within each line, sort by x-coordinate (horizontal position)
       - Standard left-to-right reading order
    
    3. y_threshold = 20 pixels (configurable)
       - Chosen based on typical text height
       - Adjust for documents with large/small fonts
    
    Why this matters:
    - Sequential mapping depends on correct order
    - Poor sorting leads to mismatched fields
    - Works for most Western language layouts
    """
```

#### 3. **pdf_processor.py** - PDF Handler
- **Purpose**: Convert PDFs to processable images
- **Responsibilities**:
  - PDF detection
  - PDF to image conversion
  - Image dimension extraction
  - Temporary file management

**Dependencies**:
- `pdf2image`: Python wrapper for poppler
- `poppler-utils`: System-level PDF rendering library

**DPI Selection Logic**:
- 300 DPI: Good balance of quality and speed
- Higher DPI = better accuracy but slower processing
- Lower DPI = faster but may miss small text

#### 4. **box_mapper.py** - Field Mapping Logic
- **Purpose**: Map detected text boxes to structured fields
- **Responsibilities**:
  - Sequential mapping implementation
  - Positional mapping implementation
  - Field validation
  - Metadata generation

**Mapping Strategies**:

##### Sequential Mapping
```
Use case: Forms with predictable field order
Algorithm:
  1. Sort boxes in reading order
  2. Assign box[i] to field[i]
  3. Track unmapped boxes (extras)

Pros: Simple, works for most forms
Cons: Fails if fields are skipped or misdetected
```

##### Positional Mapping
```
Use case: Forms with fixed layout
Algorithm:
  1. Define regions for each field (% of page)
  2. Check which region each box falls into
  3. Handle multiple boxes per region (use highest confidence)

Pros: Robust to missing fields
Cons: Requires layout knowledge upfront
```

**Complex Section - Region Matching**:

```python
# Normalize coordinates to percentages (0.0 to 1.0)
# This makes mapping resolution-independent
norm_x = center_x / image_width
norm_y = center_y / image_height

# Region format: [x_min, y_min, x_max, y_max]
# Example: [0, 0, 0.5, 0.2] = top-left quadrant
# - x: 0% to 50% of width
# - y: 0% to 20% of height

# Matching logic:
if x_min <= norm_x <= x_max and y_min <= norm_y <= y_max:
    # Box center is within the region
    matched_field = field_name
```

#### 5. **visualizer.py** - Visual Output
- **Purpose**: Create annotated images for debugging/verification
- **Responsibilities**:
  - Draw bounding boxes on images
  - Add text labels
  - Create field mapping visualizations
  - Color coding for clarity

**Visualization Types**:
1. **Box Visualization**: Shows all detected boxes with text
2. **Field Visualization**: Color-coded boxes with field names

**Why Two Visualizations?**
- Box view: Verify OCR accuracy
- Field view: Verify mapping correctness

#### 6. **output_manager.py** - Result Persistence
- **Purpose**: Save results in multiple formats
- **Responsibilities**:
  - JSON serialization
  - Human-readable text formatting
  - File naming and organization
  - Timestamp management

**Output Formats Rationale**:
- JSON: Machine-readable, structured, easy to parse
- TXT: Human-readable, quick review, no tools needed

## 🔄 Data Flow

### Complete Processing Pipeline

```
1. INPUT
   ├─ PDF File
   │  └─ Convert to images (pdf2image)
   │     └─ One image per page
   └─ Image File
      └─ Use directly

2. OCR PROCESSING (per image)
   ├─ PaddleOCR Detection
   │  └─ Detect text regions → Bounding boxes
   ├─ PaddleOCR Recognition
   │  └─ Recognize text → Text + Confidence
   └─ Post-processing
      ├─ Filter by confidence threshold
      └─ Sort in reading order

3. FIELD MAPPING
   ├─ Get image dimensions
   ├─ Apply mapping strategy
   │  ├─ Sequential: box[i] → field[i]
   │  └─ Positional: region match
   └─ Generate metadata

4. OUTPUT GENERATION
   ├─ Create visualizations
   │  ├─ Draw bounding boxes
   │  └─ Draw field labels
   ├─ Save JSON results
   └─ Save text summary

5. CLEANUP
   └─ Remove temporary PDF images
```

## 🎯 Design Patterns

### 1. **Separation of Concerns**
Each module has a single, well-defined responsibility. This makes:
- Testing easier (unit test each component)
- Maintenance simpler (changes localized)
- Code reusable (import individual modules)

### 2. **Configuration-Driven**
All tunable parameters in `config.yaml`:
- No hardcoded values in code
- Easy experimentation
- Environment-specific configs possible

### 3. **Dependency Injection**
Components receive config via constructor:
```python
def __init__(self, config: Dict):
    self.config = config
```
- Testable (mock config)
- Flexible (runtime configuration)

### 4. **Graceful Degradation**
- Missing config → Use defaults
- No text detected → Continue with warning
- Failed cleanup → Log but don't crash

## 🔧 Configuration Deep Dive

### OCR Parameters

```yaml
det_db_thresh: 0.3      # Text detection threshold
                        # Lower = more sensitive, more false positives
                        # Higher = less sensitive, may miss text
                        # Range: 0.0 to 1.0
                        # Recommended: 0.2-0.4

det_db_box_thresh: 0.6  # Bounding box quality threshold
                        # Filters out low-quality boxes
                        # Range: 0.0 to 1.0
                        # Recommended: 0.5-0.7

use_angle_cls: true     # Angle classification
                        # Enables detection of rotated text
                        # Set false for speed if text is always upright
```

### PDF Parameters

```yaml
dpi: 300               # Dots per inch for PDF rendering
                       # 150: Fast, lower quality
                       # 300: Balanced (recommended)
                       # 600: Slow, high quality

first_page: null       # Start page number (1-indexed)
                       # null = start from first page
                       # Use for large PDFs to test

last_page: null        # End page number
                       # null = process all pages
```

## 🐛 Common Issues & Solutions

### Issue: Incorrect Reading Order

**Symptom**: Fields are mapped to wrong values

**Causes**:
1. Multi-column layout
2. Text not aligned
3. Tables or complex layouts

**Solutions**:
```python
# Adjust y_threshold in ocr_engine.py
y_threshold = 30  # Increase for larger line spacing

# Or use positional mapping instead
box_mapping:
  mode: 'positional'
```

### Issue: Missing Text Detection

**Symptom**: Some text is not detected

**Causes**:
1. Low contrast
2. Small font size
3. Image quality

**Solutions**:
```yaml
# Lower detection threshold
det_db_thresh: 0.2

# Increase PDF resolution
dpi: 400

# Lower confidence filter
--confidence 0.3
```

### Issue: False Positives

**Symptom**: Detecting non-text elements

**Solutions**:
```yaml
# Increase thresholds
det_db_thresh: 0.4
det_db_box_thresh: 0.7

# Increase confidence filter
--confidence 0.7
```

## 🧪 Testing Strategy

### Unit Tests (Recommended)

```python
# test_ocr_engine.py
def test_sort_boxes_reading_order():
    """Test that boxes are sorted correctly"""
    # Create mock boxes
    # Run sort
    # Assert order

# test_box_mapper.py
def test_sequential_mapping():
    """Test sequential field assignment"""
    # Create mock boxes
    # Run mapping
    # Assert field values

# test_pdf_processor.py
def test_pdf_to_images():
    """Test PDF conversion"""
    # Use test PDF
    # Convert
    # Assert image count and quality
```

### Integration Tests

```python
def test_end_to_end():
    """Test complete pipeline"""
    # Process test document
    # Verify output files exist
    # Validate JSON structure
```

## 📦 Extending the Application

### Adding New Mapping Modes

1. **Add configuration** to `config.yaml`:
```yaml
box_mapping:
  mode: 'custom'
  custom_config:
    # Your parameters
```

2. **Implement in `box_mapper.py`**:
```python
def _map_custom(self, boxes: List[Dict]) -> Dict:
    """Your custom mapping logic"""
    pass
```

3. **Update dispatch** in `map_boxes_to_fields`:
```python
elif self.mode == 'custom':
    return self._map_custom(boxes)
```

### Adding New Output Formats

1. **Update `output_manager.py`**:
```python
def _save_csv(self, results: Dict, file_path: str):
    """Save as CSV"""
    # Implementation
```

2. **Call in `save_results`**:
```python
if self.save_csv:
    csv_path = # ...
    self._save_csv(results, csv_path)
```

### Supporting New Languages

Update `config.yaml`:
```yaml
ocr:
  lang: 'ch'  # Chinese
  # Or: 'fr', 'german', 'korean', 'japan', etc.
```

PaddleOCR supports 80+ languages out of the box.

## 🚀 Performance Optimization

### Speed Optimization

1. **Enable GPU**:
```yaml
use_gpu: true
```
Requires: CUDA-capable GPU + paddlepaddle-gpu

2. **Reduce Resolution**:
```yaml
dpi: 200  # Lower DPI for faster processing
```

3. **Disable Visualizations**:
```bash
python main.py file.pdf --no-viz
```

4. **Batch Processing**:
```python
# Process multiple files efficiently
rec_batch_num: 12  # Increase batch size
```

### Memory Optimization

1. **Process pages individually** (already implemented)
2. **Clean up temporary files** (already implemented)
3. **Use lower DPI** for large documents

### Accuracy Optimization

1. **Increase DPI**: `dpi: 400`
2. **Enable angle classification**: `use_angle_cls: true`
3. **Lower confidence threshold**: `--confidence 0.3`
4. **Use GPU** for better model performance

## 📊 Model Information

### PaddleOCR Models

**Default Models** (downloaded on first run):
- Detection: `en_PP-OCRv3_det`
- Recognition: `en_PP-OCRv3_rec`
- Angle Classifier: `ch_ppocr_mobile_v2.0_cls`

**Model Size**: ~150MB total

**Custom Models**:
You can use custom trained models:
```yaml
ocr:
  det_model_dir: '/path/to/custom_det_model'
  rec_model_dir: '/path/to/custom_rec_model'
```

## 🔒 Security Considerations

1. **File Path Validation**: 
   - Check file exists before processing
   - Validate file extensions

2. **Temporary Files**:
   - Cleaned up after processing
   - Stored in user-controlled directory

3. **No Network Calls** (after initial model download)

4. **Local Processing**: All data stays on local machine

## 📈 Metrics & Monitoring

### Key Metrics to Track

```python
# Per document
- Pages processed
- Boxes detected
- Fields mapped
- Processing time
- Confidence scores

# Aggregate
- Success rate
- Average confidence
- Common failure patterns
```

### Adding Logging

```python
import logging
logger = logging.getLogger(__name__)

# Add throughout code
logger.info("Processing started")
logger.warning("Low confidence detected")
logger.error("Processing failed")
```

## 🎓 Learning Resources

### Understanding PaddleOCR
- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddleOCR Docs](https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_en/README_en.md)

### OCR Concepts
- Text Detection: Finding where text is
- Text Recognition: Reading what the text says
- Bounding Boxes: Rectangular regions containing text

### Python Best Practices
- Type hints for clarity
- Docstrings for documentation
- Logging for debugging
- Configuration for flexibility

## 🤝 Contributing Guidelines

1. **Follow existing patterns**
2. **Add type hints** to new functions
3. **Write docstrings** with Args/Returns
4. **Add logging** for important operations
5. **Update config.yaml** for new options
6. **Update documentation** (README.md, AGENT.md)
7. **Test with real documents**

## 🔮 Future Enhancements

### Short Term
- [ ] Add confidence heat maps
- [ ] Support more output formats (CSV, XML)
- [ ] Web interface
- [ ] Progress bars for long documents

### Medium Term
- [ ] Table extraction
- [ ] Form field detection (checkboxes, signatures)
- [ ] Multi-language form support
- [ ] Batch processing CLI

### Long Term
- [ ] Custom model training pipeline
- [ ] REST API server
- [ ] Docker container
- [ ] Cloud deployment
- [ ] Real-time processing

## 📞 Developer Support

### Debugging Tips

1. **Enable debug logging**:
```bash
python main.py file.pdf --log-level DEBUG
```

2. **Check visualizations**:
   - Review `*_boxes.png` for detection issues
   - Review `*_fields.png` for mapping issues

3. **Inspect JSON output**:
   - Full box coordinates
   - Confidence scores
   - Mapping metadata

4. **Test with simple documents first**:
   - Single page
   - Clear text
   - Simple layout

### Getting Help

1. Check error messages and logs
2. Review this AGENT.md file
3. Check PaddleOCR documentation
4. Search for similar issues

---

**Last Updated**: October 2025
**Version**: 1.0
**Status**: Production Ready
