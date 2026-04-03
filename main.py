# this is our main file (run file in command: import pytesseract) -- 
# to run file: python3 main.py
# to run streamlit frontend do: streamlit run main.py 

# pip install command: pip install pytesseract pillow streamlit 

#import streamlit as st 

# Paths 
# Mac:
# pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

# Windows:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

import sys
# import streamlit as st 
try:
    import pytesseract
    from PIL import Image
except ImportError:
    print("Error: pytesseract not found. Run 'pip install pytesseract'")
    sys.exit(1)

pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

def scan_label(image_path):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text
    except Exception as e:
        return f"OCR Error: {e}"

if __name__ == "__main__":
    test_image = "sample.png" 
    print(f"--- Scanning {test_image} ---")
    
    result = scan_label(test_image)
    print("Extracted Text:")
    print("-" * 20)
    print(result)
    print("-" * 20)



