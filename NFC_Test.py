import nfc

try:
    clf = nfc.ContactlessFrontend('usb')
    if clf:
        print("🎉 NFC reader detected!")
        clf.close()
    else:
        print("❌ No NFC reader found.")
except Exception as e:
    print("❌ Error:", e)
