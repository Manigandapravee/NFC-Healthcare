import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pytesseract
from PIL import Image
from fpdf import FPDF
import sqlite3
import os
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

# --- DATABASE SETUP ---
DB_NAME = "healthcare.db"
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        uid TEXT PRIMARY KEY,
        doctor_name TEXT,
        patient_name TEXT,
        patient_number TEXT,
        patient_address TEXT,
        diagnosis TEXT,
        past_treatment TEXT,
        medications TEXT,
        prescription TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS email_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid TEXT,
        patient_name TEXT,
        recipient_email TEXT,
        file_name TEXT,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()
init_db()

# --- GUI SETUP ---
root = tk.Tk()
root.title("NFC Healthcare System")
root.geometry("500x800")

tk.Label(root, text="Scan NFC UID:").pack()
entry_uid = tk.Entry(root, width=40)
entry_uid.pack(pady=5)

form_fields = {}

def add_field(label, multiline=False):
    tk.Label(root, text=label + ":").pack()
    if multiline:
        txt = tk.Text(root, height=4, width=50)
        txt.pack()
        form_fields[label] = txt
        return txt
    else:
        ent = tk.Entry(root, width=50)
        ent.pack()
        form_fields[label] = ent
        return ent

entry_doctor_name = add_field("Doctor Name")
entry_patient_name = add_field("Patient Name")
entry_patient_number = add_field("Patient Number")
entry_patient_address = add_field("Patient Address")
txt_diagnosis = add_field("Diagnosis", multiline=True)
txt_past_treatment = add_field("Past Treatment", multiline=True)
txt_medications = add_field("Medications", multiline=True)
txt_prescription = add_field("Prescription", multiline=True)

# --- OCR Function ---
def scan_prescription_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
    if file_path:
        try:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            txt_prescription.delete("1.0", tk.END)
            txt_prescription.insert(tk.END, text)
        except Exception as e:
            messagebox.showerror("OCR Error", f"Error reading image: {e}")

# --- Export PDF (with optional email send) ---
def export_to_pdf(send_email=False):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.set_font("Arial", size=12)

        logo_path = "srm logo.png"
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=160, y=10, w=40)

        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 20, "Patient Medical Report", ln=True, align="L")
        pdf.ln(5)
        pdf.set_font("Arial", size=12)

        def draw_line():
            pdf.set_draw_color(180, 180, 180)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(4)

        def write_row(label, value):
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(50, 10, f"{label}:", border=0)
            pdf.set_font("Arial", '', 12)
            pdf.multi_cell(0, 10, value if value else "N/A", border=0)
            pdf.ln(1)

        for label, widget in form_fields.items():
            value = widget.get("1.0", tk.END).strip() if isinstance(widget, tk.Text) else widget.get()
            if value:
                write_row(label, value)
                draw_line()

        pdf.ln(10)
        pdf.set_font("Arial", 'I', 11)
        pdf.set_text_color(100, 100, 100)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.cell(0, 10, f"Generated on: {now}", ln=True, align="L")

        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, "SRM Global Hospital", ln=True, align="L")
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, "Helpline: 044 4743 2350", ln=True, align="L")

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            pdf.output(file_path)
            messagebox.showinfo("PDF Exported", f"Saved to {file_path}")
            if send_email:
                send_pdf_via_email(file_path)
    except Exception as e:
        messagebox.showerror("PDF Error", f"Could not export PDF: {e}")

# --- Logging Email Send ---
def log_email_sent(uid, patient_name, recipient_email, file_path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO email_logs (uid, patient_name, recipient_email, file_name, timestamp)
    VALUES (?, ?, ?, ?, ?)
    """, (uid, patient_name, recipient_email, os.path.basename(file_path), timestamp))
    conn.commit()
    conn.close()

# --- Send Email Function ---
def send_pdf_via_email(pdf_path):
    try:
        to_email = simpledialog.askstring("Send Email", "Enter recipient's email address:")
        if not to_email:
            return

        sender_email = "sk9024@srmist.edu.in"
        sender_password = "Abhisesha@1234"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = "Patient Medical Report - SRM Global Hospital"
        msg.attach(MIMEText("Attached is the patient's medical report.", 'plain'))

        with open(pdf_path, "rb") as f:
            attachment = MIMEApplication(f.read(), _subtype="pdf")
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
            msg.attach(attachment)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        uid = entry_uid.get().strip()
        patient_name = entry_patient_name.get()
        log_email_sent(uid, patient_name, to_email, pdf_path)

        messagebox.showinfo("Email Sent", f"PDF sent to {to_email} successfully!")
    except Exception as e:
        messagebox.showerror("Email Error", f"Could not send email: {e}")

# --- Save to DB ---
def save_to_db(uid):
    data = {
        "uid": uid,
        "doctor_name": entry_doctor_name.get(),
        "patient_name": entry_patient_name.get(),
        "patient_number": entry_patient_number.get(),
        "patient_address": entry_patient_address.get(),
        "diagnosis": txt_diagnosis.get("1.0", tk.END).strip(),
        "past_treatment": txt_past_treatment.get("1.0", tk.END).strip(),
        "medications": txt_medications.get("1.0", tk.END).strip(),
        "prescription": txt_prescription.get("1.0", tk.END).strip()
    }
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO patients VALUES (:uid, :doctor_name, :patient_name, :patient_number, :patient_address, :diagnosis, :past_treatment, :medications, :prescription)", data)
    conn.commit()
    conn.close()
    messagebox.showinfo("Saved", "Patient data saved to database.")

# --- Load from DB ---
def load_patient_data(event=None):
    uid = entry_uid.get().strip()
    if not uid:
        return
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE uid = ?", (uid,))
    row = cursor.fetchone()
    conn.close()
    if row:
        keys = list(form_fields.keys())
        for i, value in enumerate(row[1:]):  # skip UID
            widget = form_fields[keys[i]]
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
                widget.insert(tk.END, value)
            else:
                widget.delete(0, tk.END)
                widget.insert(0, value)
        messagebox.showinfo("Data Loaded", "Patient data loaded from database.")
    else:
        messagebox.showinfo("New UID", "No data found. Enter new patient details.")

# --- View Logs ---
def view_logs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM email_logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    conn.close()
    
    log_window = tk.Toplevel(root)
    log_window.title("Sent Email Logs")
    
    for idx, log in enumerate(logs):
        log_str = f"{log[4]} | UID: {log[1]} | Name: {log[2]} | To: {log[3]}"
        tk.Label(log_window, text=log_str).pack(anchor="w")

# --- Buttons ---
entry_uid.bind("<Return>", load_patient_data)

tk.Button(root, text="Scan Image Prescription", command=scan_prescription_image).pack(pady=10)
tk.Button(root, text="Save Data to Database", command=lambda: save_to_db(entry_uid.get().strip())).pack(pady=5)
tk.Button(root, text="Export as PDF", command=export_to_pdf).pack(pady=5)
tk.Button(root, text="Export PDF & Send Email", command=lambda: export_to_pdf(send_email=True)).pack(pady=5)
tk.Button(root, text="View Sent Email Logs", command=view_logs).pack(pady=5)

root.mainloop()
