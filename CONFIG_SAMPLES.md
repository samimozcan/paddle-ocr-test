# Sample Configuration Files

This directory contains example configurations for different use cases.

## 📋 Available Configurations

### 1. `config_form_processing.yaml` - Sequential Form Processing
For structured forms with fields in order (top to bottom)

### 2. `config_invoice_processing.yaml` - Positional Invoice Processing
For invoices with fixed layout

### 3. `config_high_accuracy.yaml` - High Accuracy Mode
For critical documents where accuracy is paramount

### 4. `config_fast_processing.yaml` - Fast Processing Mode
For bulk processing where speed matters

### 5. `config_multilingual.yaml` - Multi-language Documents
For documents in non-English languages

## 🔧 Usage

Copy a sample config and customize:

```bash
# Copy a sample config
cp config_samples/config_form_processing.yaml config.yaml

# Edit for your needs
nano config.yaml

# Run with custom config
python main.py document.pdf --config config.yaml
```

## 📝 Creating Custom Configs

1. Start with the default `config.yaml`
2. Copy relevant sections from samples below
3. Adjust parameters for your use case
4. Test with sample documents
5. Iterate based on results

---

## Sample 1: Form Processing (Sequential)

**Use Case**: Application forms, surveys, registration forms

**File**: `config_form_processing.yaml`

```yaml
# Form Processing Configuration
# For sequential forms with predictable field order

ocr:
  lang: 'en'
  det_db_thresh: 0.3
  det_db_box_thresh: 0.6
  use_gpu: false
  use_angle_cls: true

pdf:
  dpi: 300
  first_page: null
  last_page: null

output:
  save_visualization: true
  save_json: true
  output_dir: 'output'
  visualization_color: [0, 255, 0]

box_mapping:
  mode: 'sequential'
  sequential_fields:
    - 'firstName'
    - 'middleName'
    - 'lastName'
    - 'dateOfBirth'
    - 'email'
    - 'phone'
    - 'address'
    - 'city'
    - 'state'
    - 'zipCode'
    - 'country'
```

---

## Sample 2: Invoice Processing (Positional)

**Use Case**: Invoices, receipts, bills with fixed layout

**File**: `config_invoice_processing.yaml`

```yaml
# Invoice Processing Configuration
# For invoices with fixed layout positions

ocr:
  lang: 'en'
  det_db_thresh: 0.3
  det_db_box_thresh: 0.6
  use_gpu: false
  use_angle_cls: true

pdf:
  dpi: 300
  first_page: 1  # Usually first page only
  last_page: 1

output:
  save_visualization: true
  save_json: true
  output_dir: 'output/invoices'
  visualization_color: [0, 255, 0]

box_mapping:
  mode: 'positional'
  positional_mapping:
    # Top right corner - Invoice details
    invoiceNumber:
      region: [0.6, 0.0, 1.0, 0.15]
    invoiceDate:
      region: [0.6, 0.15, 1.0, 0.25]
    dueDate:
      region: [0.6, 0.25, 1.0, 0.35]
    
    # Top left - Vendor info
    vendorName:
      region: [0.0, 0.0, 0.5, 0.1]
    vendorAddress:
      region: [0.0, 0.1, 0.5, 0.2]
    
    # Middle left - Bill to
    customerName:
      region: [0.0, 0.25, 0.5, 0.35]
    customerAddress:
      region: [0.0, 0.35, 0.5, 0.45]
    
    # Bottom right - Totals
    subtotal:
      region: [0.6, 0.75, 1.0, 0.85]
    tax:
      region: [0.6, 0.85, 1.0, 0.90]
    total:
      region: [0.6, 0.90, 1.0, 1.0]
```

---

## Sample 3: High Accuracy Mode

**Use Case**: Legal documents, medical records, critical data

**File**: `config_high_accuracy.yaml`

```yaml
# High Accuracy Configuration
# Optimized for accuracy over speed

ocr:
  lang: 'en'
  det_db_thresh: 0.2      # Lower threshold = more sensitive
  det_db_box_thresh: 0.5  # Lower threshold = catch more boxes
  use_gpu: true           # GPU for better accuracy
  use_angle_cls: true     # Handle rotated text
  rec_batch_num: 6

pdf:
  dpi: 400                # Higher resolution
  first_page: null
  last_page: null

output:
  save_visualization: true
  save_json: true
  output_dir: 'output/high_accuracy'
  visualization_color: [0, 0, 255]  # Red for review

box_mapping:
  mode: 'sequential'
  sequential_fields:
    - 'field1'
    - 'field2'
    - 'field3'
    # Add your fields
```

**Usage:**
```bash
python main.py critical_doc.pdf --config config_high_accuracy.yaml --confidence 0.3
```

---

## Sample 4: Fast Processing Mode

**Use Case**: Bulk processing, non-critical documents, previews

**File**: `config_fast_processing.yaml`

```yaml
# Fast Processing Configuration
# Optimized for speed

ocr:
  lang: 'en'
  det_db_thresh: 0.4      # Higher threshold = faster
  det_db_box_thresh: 0.7  # Skip low-quality boxes
  use_gpu: true           # GPU for speed
  use_angle_cls: false    # Skip angle detection
  rec_batch_num: 12       # Larger batches

pdf:
  dpi: 200                # Lower resolution = faster
  first_page: null
  last_page: null

output:
  save_visualization: false  # Skip viz for speed
  save_json: true
  output_dir: 'output/batch'
  visualization_color: [0, 255, 0]

box_mapping:
  mode: 'sequential'
  sequential_fields:
    - 'field1'
    - 'field2'
    - 'field3'
```

**Usage:**
```bash
python main.py bulk_docs.pdf --config config_fast_processing.yaml --no-viz
```

---

## Sample 5: Multi-language Documents

**Use Case**: International documents, mixed language forms

**File**: `config_multilingual.yaml`

```yaml
# Multi-language Configuration
# For non-English documents

ocr:
  # Supported languages:
  # 'ch' - Chinese
  # 'en' - English
  # 'fr' - French
  # 'german' - German
  # 'korean' - Korean
  # 'japan' - Japanese
  # See: https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_en/multi_languages_en.md
  
  lang: 'ch'              # Change to your language
  det_db_thresh: 0.3
  det_db_box_thresh: 0.6
  use_gpu: false
  use_angle_cls: true
  rec_batch_num: 6

pdf:
  dpi: 300
  first_page: null
  last_page: null

output:
  save_visualization: true
  save_json: true
  output_dir: 'output/multilingual'
  visualization_color: [255, 0, 0]  # Blue

box_mapping:
  mode: 'sequential'
  sequential_fields:
    - '姓名'        # Name in Chinese
    - '地址'        # Address
    - '电话'        # Phone
    # Use field names in your language
```

---

## Sample 6: ID Card / Passport Processing

**Use Case**: Identity documents with fixed layout

**File**: `config_id_processing.yaml`

```yaml
# ID Document Processing
# For ID cards, passports, driver's licenses

ocr:
  lang: 'en'
  det_db_thresh: 0.2      # Sensitive detection
  det_db_box_thresh: 0.5
  use_gpu: false
  use_angle_cls: true     # IDs may be rotated

pdf:
  dpi: 400                # High res for small text
  first_page: 1
  last_page: 1

output:
  save_visualization: true
  save_json: true
  output_dir: 'output/ids'
  visualization_color: [0, 255, 0]

box_mapping:
  mode: 'positional'
  positional_mapping:
    # Typical ID card layout
    documentNumber:
      region: [0.0, 0.0, 0.5, 0.15]
    fullName:
      region: [0.0, 0.15, 1.0, 0.3]
    dateOfBirth:
      region: [0.0, 0.3, 0.5, 0.45]
    expiryDate:
      region: [0.5, 0.3, 1.0, 0.45]
    nationality:
      region: [0.0, 0.45, 0.5, 0.6]
    sex:
      region: [0.5, 0.45, 1.0, 0.6]
```

---

## 🔄 Switching Configurations

### Method 1: Use --config flag
```bash
python main.py doc.pdf --config config_samples/config_high_accuracy.yaml
```

### Method 2: Replace default config
```bash
cp config_samples/config_form_processing.yaml config.yaml
python main.py doc.pdf
```

### Method 3: Environment-specific configs
```bash
# Development
python main.py doc.pdf --config config_dev.yaml

# Production
python main.py doc.pdf --config config_prod.yaml
```

---

## 🎯 Choosing the Right Config

| Document Type | Recommended Config | Key Settings |
|--------------|-------------------|--------------|
| Forms (in order) | form_processing | Sequential mapping |
| Invoices | invoice_processing | Positional mapping, DPI 300 |
| Legal docs | high_accuracy | DPI 400, low thresholds |
| Bulk processing | fast_processing | DPI 200, no viz, GPU |
| Non-English | multilingual | Change lang parameter |
| IDs/Passports | id_processing | Positional, high DPI |

---

## 💡 Customization Tips

### Adjusting Detection Sensitivity

```yaml
# More sensitive (catches more text, more false positives)
det_db_thresh: 0.2
det_db_box_thresh: 0.5

# Less sensitive (faster, may miss text)
det_db_thresh: 0.4
det_db_box_thresh: 0.7
```

### Adjusting Resolution

```yaml
# Fast: 150-200 DPI
# Balanced: 250-300 DPI
# High quality: 350-400 DPI
dpi: 300
```

### Sequential vs Positional

**Use Sequential when:**
- Fields always appear in same order
- Reading order is predictable
- Form layout varies slightly

**Use Positional when:**
- Fixed layout (e.g., invoices)
- Fields may be missing
- Multi-column layouts

---

## 📚 Further Reading

- Main docs: `README.md`
- Architecture: `AGENT.md`
- Troubleshooting: `TROUBLESHOOTING.md`
- Quick start: `QUICKSTART.md`

---

**Remember**: Start with a sample config and iterate based on your results!
