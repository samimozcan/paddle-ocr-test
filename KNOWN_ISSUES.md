# Known Issues and Workarounds

## ⚠️ Segmentation Fault on macOS with Python 3.13

### Issue
When running the OCR application on macOS with Python 3.13, you may encounter a segmentation fault during OCR processing:

```
zsh: segmentation fault  ./venv/bin/python main.py
```

### Root Cause
This is a known compatibility issue with:
- PaddleOCR 3.x
- PaddlePaddle 3.x  
- Python 3.13
- macOS ARM64 architecture

The issue occurs in the C++ backend of PaddlePaddle when processing images.

### Workarounds

#### Option 1: Use Python 3.11 (Recommended)

```bash
# Install Python 3.11
brew install python@3.11

# Recreate virtual environment
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run application
python main.py "your-file.pdf"
```

#### Option 2: Use Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y poppler-utils
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

```bash
docker build -t paddle-ocr .
docker run -v $(pwd)/output:/app/output paddle-ocr "your-file.pdf"
```

#### Option 3: Use Alternative OCR Library

If you need immediate results, consider using EasyOCR or Tesseract as alternatives:

**EasyOCR:**
```bash
pip install easyocr
```

**Tesseract:**
```bash
brew install tesseract
pip install pytesseract
```

### Tracking

This issue is being tracked in:
- https://github.com/PaddlePaddle/Paddle/issues
- https://github.com/PaddlePaddle/PaddleOCR/issues

### Status

- ✅ Works: Python 3.9, 3.10, 3.11
- ❌ Segfault: Python 3.13 on macOS ARM64
- ⚠️ Unknown: Python 3.12 (not tested)

### Testing

To test if your environment will work:

```python
from paddleocr import PaddleOCR
ocr = PaddleOCR(lang='en', use_angle_cls=False)
result = ocr.ocr('test_image.png')
print("Success!" if result else "Failed")
```

If this crashes, you need to use one of the workarounds above.

---

**Last Updated:** October 21, 2025
**Affects:** macOS ARM64 + Python 3.13 + PaddleOCR 3.x
