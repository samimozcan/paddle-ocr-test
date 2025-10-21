# Quick Start Guide

Get up and running with PaddleOCR in 5 minutes!

## 🚀 Installation (First Time Only)

### Step 1: Install System Dependencies

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**Windows:**
Download poppler from: https://github.com/oschwartz10612/poppler-windows/releases/

### Step 2: Run Setup Script

```bash
cd /Users/saozcan/Projects/learn/paddle-ocr
./setup.sh
```

This will:
- Create a virtual environment
- Install all Python dependencies
- Create the output directory

### Step 3: Activate Virtual Environment

```bash
source venv/bin/activate
```

## 📝 Basic Usage

### Process a PDF

```bash
python main.py document.pdf
```

### Process an Image

```bash
python main.py photo.png
```

### With Custom Confidence Threshold

```bash
python main.py form.pdf --confidence 0.8
```

## 📤 Understanding Output

After processing, check the `output/` directory:

```
output/
├── document_20251021_143022.json          # Structured data
├── document_20251021_143022.txt           # Human-readable
├── document_page_1_boxes.png              # All detected boxes
└── document_page_1_fields.png             # Field mapping
```

### JSON Output Example

```json
{
  "fields": {
    "firstName": {
      "text": "John",
      "confidence": 0.98
    },
    "lastName": {
      "text": "Doe",
      "confidence": 0.95
    }
  }
}
```

## ⚙️ Common Customizations

### Change Detected Fields

Edit `config.yaml`:

```yaml
box_mapping:
  mode: 'sequential'
  sequential_fields:
    - 'fullName'      # Change these to match your form
    - 'email'
    - 'phone'
```

### Change Language

Edit `config.yaml`:

```yaml
ocr:
  lang: 'ch'  # Chinese
  # Or: en, french, german, korean, japan, etc.
```

### Adjust Detection Sensitivity

Edit `config.yaml`:

```yaml
ocr:
  det_db_thresh: 0.2     # Lower = more sensitive
  det_db_box_thresh: 0.5
```

## 🔍 Testing Your Setup

### 1. Check Installation

```bash
python -c "import paddleocr; print('PaddleOCR installed!')"
```

### 2. Run Examples

```bash
python examples.py
```

### 3. Check Logs

```bash
python main.py test.pdf --log-level DEBUG
```

## 🆘 Need Help?

- **No text detected?** → Lower `--confidence 0.3`
- **Wrong field mapping?** → Check visualizations in `output/`
- **Slow processing?** → Use `--no-viz` flag
- **Error messages?** → Check `TROUBLESHOOTING.md`

## 📚 Next Steps

1. Read `README.md` for full documentation
2. Check `AGENT.md` for architecture details
3. Review `examples.py` for code examples
4. Customize `config.yaml` for your use case

## 💡 Tips

- Start with simple, clear documents
- Use visualizations to debug field mapping
- Adjust confidence threshold based on document quality
- Use positional mapping for fixed-layout forms

---

**Ready to go!** 🎉 Start processing your documents!
