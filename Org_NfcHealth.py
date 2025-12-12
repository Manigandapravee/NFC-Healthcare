import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'  # or whatever `which tesseract` shows
import nfc
import json
import threading
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import datetime

# --- OCR from Image ---
def scan_prescription():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
    if file_path:
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            prescription_text.delete("1.0", tk.END)
            prescription_text.insert(tk.END, text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scan image: {str(e)}")

# --- Write to NFC Tag ---
def write_to_nfc(data):
    def on_connect(tag):
        try:
            if tag.ndef:
                json_data = json.dumps(data)
                record = nfc.ndef.TextRecord(json_data)
                tag.ndef.records = [record]
                messagebox.showinfo("Success", "Data written to NFC card successfully!")
            else:
                messagebox.showerror("Error", "NFC tag is not NDEF compatible.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write: {str(e)}")
        return True

    try:
        with nfc.ContactlessFrontend('usb') as clf:
            clf.connect(rdwr={'on-connect': on_connect})
    except Exception as e:
        messagebox.showerror("Error", f"NFC reader not found or in use: {str(e)}")

def threaded_nfc_write(data):
    thread = threading.Thread(target=write_to_nfc, args=(data,))
    thread.start()

# --- Read from NFC Tag ---
def read_from_nfc():
    def on_connect(tag):
        try:
            if tag.ndef:
                text = tag.ndef.records[0].text
                data = json.loads(text)
                fill_fields(data)
                messagebox.showinfo("Success", "Data read from NFC card successfully!")
            else:
                messagebox.showerror("Error", "NFC tag is not NDEF compatible.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read: {str(e)}")
        return True

    try:
        with nfc.ContactlessFrontend('usb') as clf:
            clf.connect(rdwr={'on-connect': on_connect})
    except Exception as e:
        messagebox.showerror("Error", f"NFC reader not found or in use: {str(e)}")

def threaded_nfc_read():
    thread = threading.Thread(target=read_from_nfc)
    thread.start()

# --- Save Form Data and Write to NFC ---
def save_data():
    data = {
        "Doctor": doctor_entry.get(),
        "Patient Name": patient_name_entry.get(),
        "Phone": phone_entry.get(),
        "Address": address_entry.get(),
        "Diagnosis": diagnosis_entry.get(),
        "Past Treatment": past_treatment_entry.get(),
        "Medications": medications_entry.get(),
        "Prescription": prescription_text.get("1.0", tk.END).strip()
    }
    if not data["Patient Name"] or not data["Doctor"]:
        messagebox.showwarning("Validation", "Please fill in at least the doctor and patient name.")
        return
    threaded_nfc_write(data)

# --- Fill Form Fields after Reading NFC ---
def fill_fields(data):
    doctor_entry.delete(0, tk.END)
    doctor_entry.insert(0, data.get("Doctor", ""))

    patient_name_entry.delete(0, tk.END)
    patient_name_entry.insert(0, data.get("Patient Name", ""))

    phone_entry.delete(0, tk.END)
    phone_entry.insert(0, data.get("Phone", ""))

    address_entry.delete(0, tk.END)
    address_entry.insert(0, data.get("Address", ""))

    diagnosis_entry.delete(0, tk.END)
    diagnosis_entry.insert(0, data.get("Diagnosis", ""))

    past_treatment_entry.delete(0, tk.END)
    past_treatment_entry.insert(0, data.get("Past Treatment", ""))

    medications_entry.delete(0, tk.END)
    medications_entry.insert(0, data.get("Medications", ""))

    prescription_text.delete("1.0", tk.END)
    prescription_text.insert(tk.END, data.get("Prescription", ""))

# --- Export Prescription and Patient Data to PDF ---
def export_to_pdf():
    filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not filename:
        return

    try:
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Patient Prescription Report")

        c.setFont("Helvetica", 12)
        y = height - 100

        fields = {
            "Doctor": doctor_entry.get(),
            "Patient Name": patient_name_entry.get(),
            "Phone": phone_entry.get(),
            "Address": address_entry.get(),
            "Diagnosis": diagnosis_entry.get(),
            "Past Treatment": past_treatment_entry.get(),
            "Medications": medications_entry.get(),
            "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Write fields to PDF
        for key, value in fields.items():
            c.drawString(50, y, f"{key}: {value}")
            y -= 20

        # Prescription text
        c.drawString(50, y - 10, "Prescription:")
        y -= 30
        text_lines = prescription_text.get("1.0", tk.END).strip().split('\n')
        for line in text_lines:
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 12)
            c.drawString(70, y, line)
            y -= 15

        c.save()
        messagebox.showinfo("PDF Exported", f"PDF saved successfully:\n{filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")

# --- GUI Setup ---
root = tk.Tk()
root.title("NFC Healthcare System")

tk.Label(root, text="Doctor Name").grid(row=0, column=0, sticky="w")
doctor_entry = tk.Entry(root, width=40)
doctor_entry.grid(row=0, column=1)

tk.Label(root, text="Patient Name").grid(row=1, column=0, sticky="w")
patient_name_entry = tk.Entry(root, width=40)
patient_name_entry.grid(row=1, column=1)

tk.Label(root, text="Phone Number").grid(row=2, column=0, sticky="w")
phone_entry = tk.Entry(root, width=40)
phone_entry.grid(row=2, column=1)

tk.Label(root, text="Address").grid(row=3, column=0, sticky="w")
address_entry = tk.Entry(root, width=40)
address_entry.grid(row=3, column=1)

tk.Label(root, text="Diagnosis").grid(row=4, column=0, sticky="w")
diagnosis_entry = tk.Entry(root, width=40)
diagnosis_entry.grid(row=4, column=1)

tk.Label(root, text="Past Treatment").grid(row=5, column=0, sticky="w")
past_treatment_entry = tk.Entry(root, width=40)
past_treatment_entry.grid(row=5, column=1)

tk.Label(root, text="Medications").grid(row=6, column=0, sticky="w")
medications_entry = tk.Entry(root, width=40)
medications_entry.grid(row=6, column=1)

tk.Label(root, text="Prescription").grid(row=7, column=0, sticky="nw")
prescription_text = tk.Text(root, height=6, width=40)
prescription_text.grid(row=7, column=1)

# --- Buttons ---
tk.Button(root, text="Scan Prescription Image", command=scan_prescription).grid(row=8, column=0, pady=10)
tk.Button(root, text="Save & Write to NFC", command=save_data).grid(row=8, column=1)
tk.Button(root, text="Read from NFC Card", command=threaded_nfc_read).grid(row=9, column=1, pady=10)
tk.Button(root, text="Export to PDF", command=export_to_pdf).grid(row=10, column=1, pady=10)

root.mainloop()
