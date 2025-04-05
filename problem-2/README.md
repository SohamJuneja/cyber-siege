
## 🚀 Overview

*AutoPay Sync* is an automated invoice processing system designed for mid-sized enterprises overwhelmed with hundreds of bills monthly. Invoices arrive via emails, scanned files, and digital formats, creating challenges in manual processing, human error, and ledger inconsistencies.

This solution automates the *extraction, **validation, and **reconciliation* of invoices from various input sources, generating a clean, structured output in CSV/Excel format.

---

## 📌 Problem

Manual processing of varied invoice formats leads to:

- Human errors (missed/duplicated entries)
- Delayed reconciliations
- Mismanagement in ledgers

The goal is to create an intelligent and extensible system that:
- Extracts critical fields from invoices using OCR and parsing techniques
- Validates consistency (e.g., total ≈ sum of line items)
- Detects duplicate bills
- Flags anomalies for manual review

---

## 🧠 Features

- 📥 *Multi-format Input Support*  
  - PDF (both text-based and scanned)
  - Image formats: JPG, PNG, TIFF
  - Email attachments (planned extension)
  - Structured formats: EDI, XML, CSV

- 🔍 *Field Extraction*
  - Vendor Name
  - Bill Number
  - Billing Date
  - Due Date
  - Total Amount
  - Line-item Descriptions

- 🛡 *Validation Engine*
  - Checks for missing critical fields
  - Verifies amount consistency
  - Identifies duplicates via bill number + vendor hash
  - Handles poor scan quality with OCR fallback and manual review triggers

- 📤 *Output*
  - Structured CSV or Excel file with extracted and validated fields

---

## 📂 Directory Structure


project_root/
├── autopay_sync.py          # Main script
├── utils/                   # Utility functions (OCR, parsers, validators)
├── test_bills/              # Sample invoices for testing
├── test_output/             # Processed output CSV
├── README.md                # Project documentation
└── requirements.txt         # Dependencies


---

## ✅ Test Cases

| Test Case | Description | Status |
|-----------|-------------|--------|
| 1. Data Extraction | Accurately parse all required fields from clean invoice | ✅ Passed |
| 2. Missing Fields | Detect and halt processing if critical fields are absent | ✅ Passed |
| 3. Duplicate Detection | Prevent duplicate bills from being logged | ✅ Passed |
| 4. Amount Consistency | Flag mismatch between total and itemized sum | ✅ Passed |
| 5. Poor Scan Handling | Try OCR, then flag for manual if unsuccessful | ✅ Passed |

---

## 🧪 How to Run

bash
git clone https://github.com/your-username/autopay-sync.git
cd autopay-sync
pip install -r requirements.txt
python autopay_sync.py


---

## 📊 Sample Output

Sample output is saved in:


test_output/processed_invoices.csv


Contains:
- Cleaned invoice data
- Flags for missing/invalid/duplicate fields

---

## 🛠 Tech Stack

- 🐍 Python 3.x
- 🧾 Tesseract OCR
- 📄 PyMuPDF, pdfplumber (PDF parsing)
- 📊 Pandas (Dataframe + Excel/CSV)
- 💡 OpenCV + PIL (Image preprocessing)

---

## 📌 Future Scope

- 📧 Email parsing integration (IMAP/SMTP)
- 🧠 ML-based invoice layout detection
- 📜 Custom rules for specific vendors
- ☁ Cloud-based processing pipeline (AWS/GCP)
- 📈 Dashboard for finance team review

---

## 👥 Team

- *Gilfoyle* – Developer & Architect  
(Feel free to add actual names and roles)

---

## 📎 References

- [Problem Statement 2 – AutoPay Sync](https://military-jaborosa-e5e.notion.site/Cyber-Siege-PRODYOGIKI-25-1ca731ebc8f780cab3b8fdec89c7af22)
- [Tesseract OCR Docs](https://github.com/tesseract-ocr/tesseract)
- [pdfplumber Documentation](https://github.com/jsvine/pdfplumber)

---