# AI-Powered P&ID to PLC Automation Platform

Upload a Piping and Instrumentation Diagram (P&ID) image. The platform detects instruments, reads their tags with OCR, generates a draft IEC 61131-3 Structured Text (PLC) program, and records every run in a tamper-evident audit ledger.

Built as a final-year Major Project (BIC786) at P.A. College of Engineering, Mangaluru, under Visvesvaraya Technological University (VTU), Belagavi.

> **Status:** Prototype. Tag extraction, draft PLC code generation and the audit ledger work end to end. See [Limitations](#limitations).
>
> **Safety:** Generated code is a draft. Never load it on real equipment without review, simulation and commissioning by a qualified control engineer.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [How It Works](#how-it-works)
4. [Results](#results)
5. [Tech Stack](#tech-stack)
6. [Project Structure](#project-structure)
7. [Requirements](#requirements)
8. [Installation](#installation)
9. [Usage](#usage)
10. [Limitations](#limitations)
11. [Standards and Compliance](#standards-and-compliance)
12. [Datasets and References](#datasets-and-references)
13. [Team](#team)
14. [License and Copyright](#license-and-copyright)

---

## Overview

Turning a P&ID into control logic is slow and error-prone. Engineers read symbols, copy tags into spreadsheets, and write PLC code by hand in separate tools. When the drawing changes, each output must be updated again.

This project joins those steps in one web workflow:

1. Upload a P&ID image (JPEG, PNG, WEBP or TIFF).
2. Detect instrument symbols and read their tags.
3. Generate a downloadable `.st` Structured Text program.
4. Log the run (drawing hash and code hash) in a hash-chained audit ledger.

The target domain is pharmaceutical manufacturing, where traceability matters.

## Features

| Feature | Status |
|---------|--------|
| Image upload and validation | Working |
| Instrument detection with annotated output | Working |
| OCR tag reading with confidence bars | Working |
| Structured Text generation (`.st` download) | Working |
| Automatic code check ("verify ok") | Working, syntax level only |
| Hash-chained audit ledger (SHA-256) | Working |

## How It Works

```
P&ID image
   |
   v
1. Detection        YOLO symbol detection
   |
   v
2. OCR              Tesseract tag reading and tag to symbol association
   |
   v
3. Code generation  Retrieval (FAISS) + Structured Text generation + check
   |
   v
4. Audit ledger     SHA-256 hash of drawing and code, chained records
```

Generation rules seen in the output for the test drawing:

| Tag type | Generated output |
|----------|------------------|
| Transmitters and elements (TT, PT, LT, TE) | REAL input, high-limit constant, BOOL alarm |
| Control valves (PCV, FCV) | Position variable clamped to 0 to 100 |
| Indicators (TI, FI, PI and similar) | Comment only, no I/O |
| Repeated tags | Numeric suffix, for example `TT_2_ALM` |

Alarm limits are placeholders (80.0) and must be set from the instrument data sheet.

## Results

Tested on 27 October 2026 with four end-to-end runs on two drawings. The main drawing is a benzene and toluene distillation sheet.

| Metric (main drawing, run 1) | Value |
|------------------------------|-------|
| Tags read | 21 |
| Mean OCR confidence | 76.4% |
| Reads with confidence 80% or higher | 10 of 21 (47.6%) |
| Reads at exactly 50% | 6 of 21 |
| Repeat run, same drawing | Same 21 tags, same code hash |
| Audit ledger after 4 runs | Chain valid, 4 records |

These numbers are the platform's own confidence values. No ground-truth labels were prepared, so detection precision and recall are not reported.

## Tech Stack

| Area | Tools |
|------|-------|
| Backend | Python, FastAPI |
| Frontend | React, TypeScript |
| Detection | YOLOv8 (Ultralytics) |
| OCR | Tesseract |
| Retrieval | FAISS, LangChain |
| Audit | SHA-256 hash-chained ledger |
| Deployment | Docker |
| Training | Google Colab (T4 GPU) |

The report also specifies CRAFT text detection, PostgreSQL, Tailwind CSS and a GPT-family or local Llama 3 model. Check which of these are in your final code before keeping them here.

## Project Structure

> Edit this tree to match the real repository.

```
P-ID-TO-PLC-AUTOMATION/
|-- backend/
|   |-- main.py                # FastAPI app
|   |-- ocr_service.py         # OCR and tag extraction
|   |-- postprocess.py         # Symbol and tag association
|   |-- plc_corpus.py          # Reference PLC patterns
|   |-- retrieval_service.py   # FAISS retrieval
|   |-- codegen_service.py     # Structured Text generation
|   |-- verify_service.py      # Generated code check
|-- frontend/                  # React and TypeScript web app
|-- pid_model/
|   |-- pid_new_run/weights/best.pt
|-- docs/                      # Project report and logbook
|-- requirements.txt
|-- LICENSE
|-- README.md
```

## Requirements

**Software**

- Python 3.10 or newer
- Node.js 18 or newer and npm
- Tesseract OCR
- Git
- Docker (optional)

**Hardware**

- Inference runs on a normal laptop.
- A GPU is needed only to retrain the model (training used a Colab T4).

Python packages are in `requirements.txt`. Main ones: `fastapi`, `uvicorn`, `ultralytics`, `pytesseract`, `faiss-cpu`, `langchain`, `scikit-learn`, `opencv-python`.

## Installation

**1. Clone**

```bash
git clone https://github.com/Muhammedkp12/P-ID-TO-PLC-AUTOMATION.git
cd P-ID-TO-PLC-AUTOMATION
```

**2. Install Tesseract**

```bash
# Ubuntu or Debian
sudo apt install tesseract-ocr

# macOS
brew install tesseract

# Windows: install from the Tesseract project page and add it to PATH
```

**3. Backend**

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**4. Model weights**

Place the trained weights at `pid_model/pid_new_run/weights/best.pt`.

> Use `pid_new_run`. The older `pid_final_run` folder is corrupted.

**5. Frontend**

```bash
cd frontend
npm install
```

**6. Secrets**

If you use a hosted language model, put keys in a `.env` file. Never commit it.

## Usage

**Start the backend**

```bash
uvicorn main:app --reload
```

API docs: `http://localhost:8000/docs`

**Start the frontend**

```bash
cd frontend
npm start
```

**Run the pipeline**

1. Open the web app and wait for the "Model loaded" status.
2. Upload a P&ID image.
3. Check the annotated drawing. Tags with amber confidence bars need a manual check.
4. Review the generated Structured Text and download the `.st` file.
5. Open the audit trail to see the run and the chain status.

> Replace `main:app` and the start commands with the ones your project uses.

## Limitations

- **Small test set.** One main drawing (21 tags) and one other drawing (12 tags).
- **No ground truth.** Detection precision, recall and tag association accuracy are unknown. OCR confidence is not the same as correctness.
- **OCR misreads.** Short function codes inside small bubbles (TI, PI, FI) are easily confused. Several 50% reads look like misreads.
- **Not a pharmaceutical drawing.** The main test sheet is a general chemical process drawing.
- **Run difference not explained.** Run 0 and run 1 used the same drawing but read 15 and 21 tags.
- **Code not compiled.** Output was not tested in a vendor PLC environment or simulator. "verify ok" is a syntax level check.
- **Audit scope.** Tested with an anonymous user and one action type. User roles were not tested. A hash chain gives tamper evidence, not regulatory compliance.
- **Detection accuracy.** The YOLOv8n model (trained on Digitize-PID, 100 epochs) reached mAP50 of about 0.30, which is below production grade.

## Standards and Compliance

Used as design references: ISA-5.1, IEC 61131-3, ISA-88, GAMP 5, GMP and FDA 21 CFR Part 11.

This is a student research prototype. It has not been validated for regulated use, and no compliance claim is made.

## Datasets and References

- Digitize-PID: S. Paliwal, A. Jain, M. Sharma, L. Vig, arXiv:2109.03794 (2021). Dataset on Hugging Face as `hamzas/digitize-pid-yolo`.
- PID2Graph: Zenodo record 14803338.
- Koziolek et al., "LLM-based and Retrieval-Augmented Control Code Generation," LLM4Code 2024.
- Fakih et al., "LLM4PLC: Harnessing Large Language Models for Verifiable Programming of PLCs," ICSE-SEIP 2024.
- Kim et al., "Automated inspection of P&ID object recognition using deep learning," Scientific Reports, 2025.

The full list of 13 references is in the project report in `docs/`. Check each dataset's license before reuse.

## Team

Department of Computer Science and Engineering (IoT and Cyber Security including Blockchain Technology), P.A. College of Engineering, Mangaluru, 2026 to 2027.

| Name | Role |
|------|------|
| Mariyamathul Kaizarana | AI models, OCR, code generation, backend |
| Muhammed K.P. | Frontend and web application |
| Rawana K.M. | Documentation |

**Guide:** Dr. Shamna N. V.

## License and Copyright

Copyright (c) 2026 Mariyamathul Kaizarana, Muhammed K.P. and Rawana K.M. Released under the **MIT License**. See [LICENSE](LICENSE).

Third-party components keep their own licenses:

| Component | License |
|-----------|---------|
| Ultralytics YOLOv8 | AGPL-3.0 (check before commercial use) |
| Tesseract OCR | Apache-2.0 |
| FAISS | MIT |
| FastAPI | MIT |
| Datasets | See each dataset page |

Project report and documents in `docs/` are submitted to VTU as academic work. Check with your institution before changing their license.

### Citation

```
M. Kaizarana, Muhammed K.P., R. K.M., "AI-Powered P&ID to PLC Automation Platform,"
B.E. Major Project, P.A. College of Engineering, VTU, 2026.
```

## Disclaimer

Provided as is, without warranty. Do not use generated PLC code on live industrial equipment without review and testing by a qualified engineer.
