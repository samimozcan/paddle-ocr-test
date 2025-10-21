# Troubleshooting Guide

Common issues and their solutions.

## 🔴 Installation Issues

### Error: "pdf2image module not found"

**Solution:**
```bash
pip install pdf2image
```

If still failing:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Error: "Unable to get page count. Is poppler installed?"

**Cause:** Poppler is not installed or not in PATH

**Solution:**

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install poppler-utils
```

**Windows:**
1. Download poppler from: https://github.com/oschwartz10612/poppler-windows/releases/
2. Extract to `C:\Program Files\poppler`
3. Add `C:\Program Files\poppler\bin` to PATH

**Verify installation:**
```bash
pdfinfo -v
```

### Error: "No module named 'paddleocr'"

**Solution:**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Install PaddleOCR
pip install paddleocr>=2.7.0
```

### Error: "Failed to download models"

**Cause:** Network issues or firewall blocking model downloads

**Solution:**
1. Check internet connection
2. Try again (download may have timed out)
3. Use VPN if behind firewall
4. Manually download models: https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_en/models_list_en.md

## 🟡 Processing Issues

### Issue: No text detected

**Symptoms:**
```
⚠️  No text detected on page 1
```

**Possible Causes & Solutions:**

1. **Low image quality**
   ```yaml
   # In config.yaml, increase PDF resolution
   pdf:
     dpi: 400  # or 600
   ```

2. **Text too small or faint**
   ```yaml
   # Lower detection thresholds
   ocr:
     det_db_thresh: 0.2
     det_db_box_thresh: 0.5
   ```

3. **Non-standard language**
   ```yaml
   # Set correct language
   ocr:
     lang: 'ch'  # or your language
   ```

4. **Low confidence threshold**
   ```bash
   python main.py file.pdf --confidence 0.3
   ```

### Issue: Detected text is incorrect

**Symptoms:**
- Text recognized but wrong characters
- Numbers mixed up
- Symbols misread

**Solutions:**

1. **Increase image resolution**
   ```yaml
   pdf:
     dpi: 400
   ```

2. **Enable angle classification**
   ```yaml
   ocr:
     use_angle_cls: true
   ```

3. **Use GPU for better accuracy**
   ```yaml
   ocr:
     use_gpu: true
   ```
   (Requires CUDA-capable GPU)

4. **Check language setting**
   ```yaml
   ocr:
     lang: 'en'  # Make sure this matches your document
   ```

### Issue: Wrong field mapping

**Symptoms:**
- firstName contains lastName value
- Fields out of order
- Missing fields

**Solutions:**

1. **Check visualizations**
   ```bash
   # Look at the field mapping visualization
   open output/document_page_1_fields.png
   ```

2. **Adjust reading order threshold**
   ```python
   # Edit ocr_engine.py, line ~95
   y_threshold = 30  # Increase if multi-line fields
   ```

3. **Switch to positional mapping**
   ```yaml
   box_mapping:
     mode: 'positional'
     positional_mapping:
       firstName:
         region: [0, 0, 0.5, 0.2]
       lastName:
         region: [0.5, 0, 1.0, 0.2]
   ```

4. **Add more fields**
   ```yaml
   sequential_fields:
     - 'title'        # Add missing fields
     - 'firstName'
     - 'lastName'
   ```

### Issue: Detecting unwanted elements

**Symptoms:**
- Logos, images, borders detected as text
- Page numbers included
- Headers/footers captured

**Solutions:**

1. **Increase thresholds**
   ```yaml
   ocr:
     det_db_thresh: 0.4
     det_db_box_thresh: 0.7
   ```

2. **Increase confidence filter**
   ```bash
   python main.py file.pdf --confidence 0.8
   ```

3. **Use positional mapping** to exclude regions
   ```yaml
   box_mapping:
     mode: 'positional'
     # Only define regions where actual fields are
   ```

## 🟢 Performance Issues

### Issue: Slow processing

**Solutions:**

1. **Disable visualizations**
   ```bash
   python main.py file.pdf --no-viz
   ```

2. **Lower PDF resolution**
   ```yaml
   pdf:
     dpi: 200  # Faster but less accurate
   ```

3. **Enable GPU**
   ```yaml
   ocr:
     use_gpu: true
   ```

4. **Increase batch size**
   ```yaml
   ocr:
     rec_batch_num: 12
   ```

5. **Process specific pages only**
   ```yaml
   pdf:
     first_page: 1
     last_page: 3
   ```

### Issue: Out of memory

**Symptoms:**
```
MemoryError: Unable to allocate array
```

**Solutions:**

1. **Reduce PDF resolution**
   ```yaml
   pdf:
     dpi: 150
   ```

2. **Process fewer pages at once**
   ```yaml
   pdf:
     first_page: 1
     last_page: 10  # Process in batches
   ```

3. **Close other applications**

4. **Disable angle classification**
   ```yaml
   ocr:
     use_angle_cls: false
   ```

## 🔵 File Issues

### Error: "File not found"

**Check:**
1. File path is correct
2. File exists: `ls -la your-file.pdf`
3. Use absolute path: `/full/path/to/file.pdf`
4. Check permissions: `chmod 644 your-file.pdf`

### Error: "Failed to open PDF"

**Causes:**
- Encrypted PDF
- Corrupted file
- Unsupported PDF version

**Solutions:**
1. Try opening in PDF viewer
2. Re-save PDF
3. Remove password protection
4. Convert to images first

### Error: "Permission denied"

**Solution:**
```bash
# Make script executable
chmod +x main.py

# Check file permissions
ls -la your-file.pdf

# Fix permissions if needed
chmod 644 your-file.pdf
```

## 🟣 Configuration Issues

### Error: "Config file not found"

**Solution:**
```bash
# Check config.yaml exists
ls -la config.yaml

# Create if missing
cp config.yaml.example config.yaml

# Or use custom config
python main.py file.pdf --config my_config.yaml
```

### Issue: Config changes not working

**Check:**
1. YAML syntax is correct (spaces, not tabs)
2. Config file is being loaded (check logs)
3. Restart application after changes
4. No typos in field names

**Validate YAML:**
```bash
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

## 🔧 Debug Commands

### Check environment

```bash
# Python version
python --version

# Installed packages
pip list | grep -i "paddle\|pdf2image\|pillow"

# Poppler
which pdfinfo
pdfinfo -v

# Virtual environment active?
which python
```

### Enable debug logging

```bash
python main.py file.pdf --log-level DEBUG
```

### Test OCR engine

```python
python
>>> from paddleocr import PaddleOCR
>>> ocr = PaddleOCR(lang='en')
>>> result = ocr.ocr('test_image.png')
>>> print(result)
```

### Test PDF conversion

```python
python
>>> from pdf2image import convert_from_path
>>> images = convert_from_path('test.pdf')
>>> print(f"Converted {len(images)} pages")
```

## 📞 Getting Help

### Before asking for help:

1. ✅ Check this troubleshooting guide
2. ✅ Read error messages carefully
3. ✅ Enable debug logging
4. ✅ Test with a simple document
5. ✅ Check visualizations

### When reporting issues:

Include:
- Operating system and version
- Python version: `python --version`
- Error message (full text)
- Command used
- Document type (PDF/image)
- Config.yaml settings (if relevant)
- Debug log output

### Resources:

- **PaddleOCR Issues**: https://github.com/PaddlePaddle/PaddleOCR/issues
- **pdf2image Issues**: https://github.com/Belval/pdf2image/issues
- **Project Documentation**: README.md, AGENT.md

## 🎯 Common Workflows

### Workflow: Testing new document type

```bash
# 1. Start with default settings
python main.py test.pdf

# 2. Check visualizations
open output/test_page_1_fields.png

# 3. If mapping wrong, try positional
# Edit config.yaml -> mode: 'positional'

# 4. If detection poor, adjust thresholds
# Edit config.yaml -> det_db_thresh: 0.2

# 5. Re-run and compare
python main.py test.pdf

# 6. Iterate until satisfied
```

### Workflow: Optimizing for speed

```bash
# 1. Baseline
time python main.py large.pdf

# 2. Disable viz
time python main.py large.pdf --no-viz

# 3. Lower DPI (config.yaml: dpi: 200)
time python main.py large.pdf --no-viz

# 4. Process sample pages
# config.yaml: first_page: 1, last_page: 5
time python main.py large.pdf --no-viz
```

### Workflow: Improving accuracy

```bash
# 1. Baseline with debug
python main.py doc.pdf --log-level DEBUG

# 2. Increase resolution
# config.yaml: dpi: 400

# 3. Lower confidence
python main.py doc.pdf --confidence 0.3

# 4. Check language setting
# config.yaml: lang: 'en'

# 5. Enable angle classification
# config.yaml: use_angle_cls: true

# 6. Compare results
python main.py doc.pdf
```

---

**Still stuck?** Review AGENT.md for architectural details or post an issue with debug logs.
