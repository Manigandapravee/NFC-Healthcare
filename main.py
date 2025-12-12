import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import pytesseract
from smartcard.System import readers
from smartcard.util import toBytes, toHexString
from reportlab.pdfgen import canvas

pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'  # Update path as needed

# GUI Window
window = tk.Tk()
window.title("NFC Healthcare System")

fields = {}
field_names = [
    "Doctor Name", "Patient Name", "Phone Number", "Address",
    "Diagnosis", "Past Treatment", "Medications", "Prescription"
]

for i, field in enumerate(field_names):
    label = tk.Label(window, text=field)
    label.grid(row=i, column=0, sticky="w")
    entry = tk.Text(window, height=2, width=50)
    entry.grid(row=i, column=1)
    fields[field] = entry

def scan_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
    if file_path:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        fields["Prescription"].delete('1.0', tk.END)
        fields["Prescription"].insert(tk.END, text)

def get_all_text():
    return {key: field.get("1.0", tk.END).strip() for key, field in fields.items()}

def create_pdf(data):
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf")
    if not file_path:
        return
    pdf = canvas.Canvas(file_path)
    y = 800
    for key, value in data.items():
        pdf.drawString(50, y, f"{key}: {value}")
        y -= 20
    pdf.save()
    messagebox.showinfo("PDF", "PDF exported successfully.")

def write_to_card(data):
    try:
        r = readers()
        if len(r) == 0:
            messagebox.showerror("NFC Error", "No NFC reader detected.")
            return
        reader = r[0]
        connection = reader.createConnection()
        connection.connect()

        # Encode data into bytes (cut to fit if needed)
        combined_data = '|'.join(data.values())[:240]  # Max ~240 bytes
        byte_data = combined_data.encode('utf-8')

        # Write in chunks of 16 bytes (block size)
        for i in range(0, len(byte_data), 16):
            chunk = byte_data[i:i+16]
            block = i // 16
            apdu = [0xFF, 0xD6, 0x00, block, len(chunk)] + list(chunk)
            response, sw1, sw2 = connection.transmit(apdu)
            if sw1 != 0x90:
                raise Exception(f"Write failed at block {block}")
        messagebox.showinfo("NFC Write", "Data written to NFC card.")
    except Exception as e:
        messagebox.showerror("NFC Error", str(e))

def read_from_card():
    try:
        r = readers()
        if len(r) == 0:
            messagebox.showerror("NFC Error", "No NFC reader found.")
            return
        reader = r[0]
        connection = reader.createConnection()
        connection.connect()

        result = bytearray()
        for block in range(15):  # Read first 15 blocks
            apdu = [0xFF, 0xB0, 0x00, block, 16]
            response, sw1, sw2 = connection.transmit(apdu)
            if sw1 == 0x90:
                result += bytearray(response)
            else:
                break

        decoded = result.decode('utf-8', errors='ignore')
        parts = decoded.split('|')
        for i, key in enumerate(fields.keys()):
            fields[key].delete("1.0", tk.END)
            if i < len(parts):
                fields[key].insert(tk.END, parts[i])
        messagebox.showinfo("NFC Read", "Data read from NFC card.")
    except Exception as e:
        messagebox.showerror("NFC Error", str(e))

# Buttons
tk.Button(window, text="Scan Image Prescription", command=scan_image).grid(row=9, column=0, pady=10)
tk.Button(window, text="Write to NFC", command=lambda: write_to_card(get_all_text())).grid(row=9, column=1)
tk.Button(window, text="Read from NFC", command=read_from_card).grid(row=10, column=0)
tk.Button(window, text="Export as PDF", command=lambda: create_pdf(get_all_text())).grid(row=10, column=1)

window.mainloop()
