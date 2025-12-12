# NFC Healthcare System

The **NFC Healthcare System** is a Python-based application that allows hospitals to
store, read, and manage patient information using **NFC (Near Field Communication)**,
along with OCR-based prescription scanning, PDF report generation, and email export.

This project includes:
- NFC-based patient identification
- OCR (Tesseract) to extract text from prescriptions
- PDF patient health report generator
- SQLite database for storing patient records
- Email export of patient reports
- GUI built using Tkinter

---

## 📌 Features
### 🔹 1. NFC Integration
- Read patient UID from NFC card
- Use UID to fetch patient data  
- Store patient medical details linked to NFC tag

### 🔹 2. OCR Prescription Scanning
- Upload or scan image
- Extract text using **pytesseract**
- Auto-fill patient diagnosis/medication fields

### 🔹 3. PDF Report Generation
- Automatically generate health reports in PDF format
- Includes patient details, diagnosis, medication, and prescription

### 🔹 4. Email Sending
- Send PDF report to any email address
- SMTP Gmail integration with app password

### 🔹 5. Database
- SQLite database (`healthcare.db`)
- Patient details auto-saved and retrieved

---

## 📂 Project Structure


---

## 🔧 Installation

### 1️⃣ Install dependencies


### 2️⃣ Install Tesseract OCR  
- Windows: Install from https://github.com/tesseract-ocr/tesseract  
- macOS: `brew install tesseract`  
- Ubuntu: `sudo apt install tesseract-ocr`

---

## ▶️ Running the Application

The app opens a GUI window where you can:
- Scan NFC card  
- Enter patient details  
- Upload prescription image  
- Generate PDF  
- Send email  

---

## 🔐 Email Configuration (IMPORTANT)
Set environment variables locally (do not upload to GitHub):


In Python, your code should use:

```python
import os
SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")






