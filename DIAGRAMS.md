# System Flow Diagrams

Visual representations of how the OCR application works.

## 📊 Overall System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                               │
│                  (PDF or Image File Path)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MAIN APPLICATION                            │
│                        (main.py)                                 │
│  • Parse CLI arguments                                           │
│  • Load configuration                                            │
│  • Initialize components                                         │
│  • Orchestrate processing pipeline                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────┴────────┐
                    │  Is it a PDF?   │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │ YES                     NO  │
              ▼                             ▼
    ┌─────────────────┐          ┌──────────────────┐
    │ PDF PROCESSOR   │          │  Use image       │
    │ pdf_processor.py│          │  directly        │
    │                 │          └──────────────────┘
    │ • Convert PDF   │                   │
    │   to images     │                   │
    │ • One per page  │                   │
    └────────┬────────┘                   │
             │                             │
             └──────────────┬──────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │  FOR EACH PAGE/IMAGE        │
              └─────────────┬───────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │      OCR ENGINE             │
              │     ocr_engine.py           │
              │                             │
              │  1. Detect text regions     │
              │  2. Recognize text          │
              │  3. Extract bounding boxes  │
              │  4. Calculate confidence    │
              │  5. Filter low confidence   │
              │  6. Sort in reading order   │
              └─────────────┬───────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  Raw Boxes    │
                    │  with Text    │
                    └───────┬───────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │      BOX MAPPER             │
              │     box_mapper.py           │
              │                             │
              │  • Map boxes to fields      │
              │  • Sequential or Positional │
              │  • Generate metadata        │
              └─────────────┬───────────────┘
                            │
                            ▼
                  ┌─────────────────┐
                  │ Structured Data │
                  │ (Fields mapped) │
                  └─────────┬───────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
    ┌─────────────────┐        ┌──────────────────┐
    │   VISUALIZER    │        │  OUTPUT MANAGER  │
    │  visualizer.py  │        │ output_manager.py│
    │                 │        │                  │
    │ • Draw boxes    │        │ • Save JSON      │
    │ • Add labels    │        │ • Save TXT       │
    │ • Create PNGs   │        │ • Format results │
    └────────┬────────┘        └────────┬─────────┘
             │                           │
             └───────────┬───────────────┘
                         │
                         ▼
           ┌─────────────────────────────┐
           │      OUTPUT DIRECTORY        │
           │                              │
           │  • document.json             │
           │  • document.txt              │
           │  • document_boxes.png        │
           │  • document_fields.png       │
           └──────────────────────────────┘
```

## 🔄 Data Flow Detail

```
INPUT: document.pdf
    │
    ├─► [PDF Processor] ──► image_page_1.png ─┐
    │                       image_page_2.png  │
    │                       image_page_3.png  │
    │                                          │
    └──────────────────────────────────────────┘
                                               │
    ┌──────────────────────────────────────────┘
    │
    └─► [OCR Engine]
         │
         ├─► Detection: Find text regions
         │   └─► Box 1: [[100,50], [200,50], [200,80], [100,80]]
         │       Box 2: [[100,90], [200,90], [200,120], [100,120]]
         │
         ├─► Recognition: Read text
         │   └─► Box 1: "John" (confidence: 0.98)
         │       Box 2: "Doe" (confidence: 0.95)
         │
         └─► Post-process
             ├─► Filter: Remove low confidence
             └─► Sort: Reading order (top→bottom, left→right)
                 │
                 └─► [Sorted Boxes]
                      │
                      └─► [Box Mapper]
                           │
                           ├─► Sequential Mode:
                           │   • Box[0] → firstName
                           │   • Box[1] → lastName
                           │   • Box[2] → email
                           │
                           ├─► Positional Mode:
                           │   • Box in region[0,0,0.5,0.2] → firstName
                           │   • Box in region[0.5,0,1,0.2] → lastName
                           │
                           └─► [Mapped Result]
                                {
                                  "fields": {
                                    "firstName": {
                                      "text": "John",
                                      "confidence": 0.98
                                    }
                                  }
                                }
```

## 🗺️ Box Mapping Strategies

### Sequential Mapping
```
Document:              Reading Order:           Mapping:
┌──────────┐          1. "John"                firstName: "John"
│  John    │  ───►    2. "Doe"         ───►    lastName: "Doe"
│  Doe     │          3. "john@..."            email: "john@..."
│  john@...|          4. "555-1234"            phone: "555-1234"
│  555-1234│
└──────────┘

Configuration:
box_mapping:
  mode: 'sequential'
  sequential_fields:
    - 'firstName'
    - 'lastName'
    - 'email'
    - 'phone'
```

### Positional Mapping
```
Document Grid (0-1 normalized):

0,0 ─────────────────── 1,0
 │   ┌─────┬─────┐      │
 │   │John │ Doe │      │
 │   └─────┴─────┘      │
 │   ┌──────────┐       │
 │   │john@...  │       │
 │   └──────────┘       │
 │   ┌──────────┐       │
 │   │555-1234  │       │
 │   └──────────┘       │
0,1 ─────────────────── 1,1

Region Mapping:
firstName:  [0.0, 0.0, 0.5, 0.2]  ← Top-left
lastName:   [0.5, 0.0, 1.0, 0.2]  ← Top-right
email:      [0.0, 0.2, 1.0, 0.4]  ← Middle
phone:      [0.0, 0.4, 1.0, 0.6]  ← Lower

Configuration:
box_mapping:
  mode: 'positional'
  positional_mapping:
    firstName:
      region: [0.0, 0.0, 0.5, 0.2]
    lastName:
      region: [0.5, 0.0, 1.0, 0.2]
```

## 🔧 Component Interaction

```
┌─────────────────────────────────────────────────────────┐
│                    Configuration                         │
│                     (config.yaml)                        │
│  • OCR parameters                                        │
│  • Field definitions                                     │
│  • Output settings                                       │
└─────────────────┬───────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬─────────────┬───────────┐
    │             │             │             │           │
    ▼             ▼             ▼             ▼           ▼
┌────────┐  ┌──────────┐  ┌─────────┐  ┌────────┐  ┌────────┐
│  OCR   │  │   PDF    │  │   Box   │  │Visual- │  │ Output │
│ Engine │  │Processor │  │  Mapper │  │ izer   │  │Manager │
└────────┘  └──────────┘  └─────────┘  └────────┘  └────────┘
     │            │             │            │            │
     └────────────┴─────────────┴────────────┴────────────┘
                             │
                    Data flows between
                      components via
                    standardized dicts
```

## 📦 Module Dependencies

```
main.py
  ├── imports ocr_engine
  ├── imports pdf_processor
  ├── imports box_mapper
  ├── imports visualizer
  ├── imports output_manager
  └── uses config.yaml

ocr_engine.py
  ├── paddleocr (external)
  └── numpy (external)

pdf_processor.py
  ├── pdf2image (external)
  └── PIL (external)

box_mapper.py
  └── (no external deps)

visualizer.py
  ├── cv2 (external)
  └── numpy (external)

output_manager.py
  ├── json (stdlib)
  └── datetime (stdlib)
```

## 🎯 Processing Decision Tree

```
Start
  │
  ├─► Load config ──► Config exists? ─┬─► Yes ──► Use config
  │                                   └─► No ──► Use defaults
  │
  ├─► Check file type
  │    │
  │    ├─► PDF? ──► Yes ──► Convert to images ──┐
  │    └─► Image? ──► Yes ──► Use directly ─────┤
  │                                              │
  └─────────────────────────────────────────────┘
                                                 │
  ┌──────────────────────────────────────────────┘
  │
  ├─► Run OCR ──► Boxes detected? ─┬─► Yes ──► Continue
  │                                 └─► No ──► Log warning, skip
  │
  ├─► Filter boxes ──► Confidence > threshold? ─┬─► Yes ──► Keep
  │                                              └─► No ──► Discard
  │
  ├─► Sort boxes ──► Reading order
  │
  ├─► Map to fields ──► Mapping mode?
  │    │
  │    ├─► Sequential ──► Assign by order
  │    └─► Positional ──► Assign by location
  │
  ├─► Create visualizations? ─┬─► Yes ──► Generate PNGs
  │                            └─► No ──► Skip
  │
  ├─► Save results ──► JSON + TXT
  │
  └─► Cleanup temp files ──► Done
```

## 🏗️ File Structure Flow

```
User runs: python main.py document.pdf

1. Input
   document.pdf

2. Temp Processing (if PDF)
   temp_images/
   ├── document_page_1.png
   ├── document_page_2.png
   └── document_page_3.png

3. OCR Processing
   (In memory)
   • Detected boxes
   • Recognized text
   • Confidence scores

4. Output Generation
   output/
   ├── document_20251021_143022.json
   ├── document_20251021_143022.txt
   ├── document_page_1_boxes.png
   ├── document_page_1_fields.png
   ├── document_page_2_boxes.png
   └── document_page_2_fields.png

5. Cleanup
   temp_images/ → Deleted
```

## 🎨 Visualization Examples

### Bounding Box Visualization
```
Original Image:          With Bounding Boxes:
┌──────────────┐        ┌──────────────┐
│              │        │  ┌────────┐  │ ← Green box
│  John Doe    │   ───► │  │John Doe│  │   + text label
│              │        │  └────────┘  │   + confidence
│  Email:      │        │  ┌────────┐  │
│  john@...    │        │  │Email:  │  │
│              │        │  │john@...│  │
└──────────────┘        │  └────────┘  │
                        └──────────────┘
```

### Field Mapping Visualization
```
Original Image:          With Field Labels:
┌──────────────┐        ┌──────────────┐
│              │        │  firstName   │ ← Different colors
│  John Doe    │   ───► │  ┌────┐     │   per field
│              │        │  │John│     │
│  Email:      │        │  └────┘     │
│  john@...    │        │  email      │
│              │        │  ┌────────┐ │
└──────────────┘        │  │john@...│ │
                        │  └────────┘ │
                        └──────────────┘
```

## 🔢 Data Transformation

```
Stage 1: Raw OCR Output
[
  {
    "box": [[100,50], [200,50], [200,80], [100,80]],
    "text": "John",
    "confidence": 0.98
  },
  ...
]

Stage 2: Sorted & Filtered
[
  {
    "box": [[100,50], ...],
    "text": "John",
    "confidence": 0.98,
    "position": {
      "center_x": 150,
      "center_y": 65,
      ...
    }
  },
  ...
]

Stage 3: Mapped to Fields
{
  "fields": {
    "firstName": {
      "text": "John",
      "confidence": 0.98,
      "box": [[100,50], ...]
    },
    ...
  },
  "metadata": {
    "total_boxes": 5,
    "mapped_fields": 3,
    ...
  }
}

Stage 4: Final Output (JSON)
{
  "input_file": "document.pdf",
  "total_pages": 1,
  "pages": [{
    "page_number": 1,
    "mapped_result": { ... },
    "raw_boxes": [ ... ]
  }]
}
```

## 🚀 Execution Timeline

```
Time    Action                      Component
──────────────────────────────────────────────────
0ms     Parse arguments             main.py
10ms    Load config                 main.py
50ms    Initialize PaddleOCR        ocr_engine.py
        (Model loading)             
500ms   Convert PDF → images        pdf_processor.py
1500ms  OCR on page 1              ocr_engine.py
        • Detection
        • Recognition
2000ms  Sort & filter boxes         ocr_engine.py
2100ms  Map to fields               box_mapper.py
2200ms  Create visualizations       visualizer.py
2500ms  Save outputs                output_manager.py
2600ms  Cleanup temp files          pdf_processor.py
2650ms  Done! ✓
```

---

These diagrams illustrate the complete flow of data and control through the OCR application. Use them to understand how components interact and where to make modifications.

**Key Takeaways:**
- Modular design with clear separation of concerns
- Data flows linearly through the pipeline
- Each component has a single, well-defined responsibility
- Configuration drives behavior throughout
- Temporary files are created and cleaned up automatically
