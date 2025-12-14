import os
import requests
from fpdf import FPDF

# --- CONFIGURATION ---
# Paths are relative to where you run the script
SOURCE_DIR = os.path.join("BazaAll", "Українська", "Крок Б", "Лабораторна діагностика")
OUTPUT_DIR = os.path.join("BazaAll", "Українська", "Крок Б")
OUTPUT_FILENAME = "Merged_Lab_Diagnostics"
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/notosans/NotoSans-Regular.ttf"
FONT_FILE = "NotoSans-Regular.ttf"

def download_font():
    """Downloads a Cyrillic-compatible font for the PDF."""
    if not os.path.exists(FONT_FILE):
        print(f"Downloading font for PDF support...")
        r = requests.get(FONT_URL)
        with open(FONT_FILE, 'wb') as f:
            f.write(r.content)

def clean_text(text):
    """Sanitizes text for PDF generation."""
    # Replace characters that might break Latin-1/Unicode mapping in older readers
    return text.replace('\u2013', '-').replace('\u2014', '-').replace('\u2019', "'")

def main():
    # 1. Verify Paths
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory not found: {SOURCE_DIR}")
        return
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 2. Collect Files
    txt_files = []
    for root, dirs, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(os.path.join(root, file))
    
    txt_files.sort() # Sort to ensure consistent order
    
    if not txt_files:
        print("No .txt files found to merge.")
        return

    print(f"Found {len(txt_files)} files. Merging...")

    # 3. Prepare PDF
    download_font()
    pdf = FPDF()
    pdf.add_page()
    
    # Add font (Unicode support)
    pdf.add_font('NotoSans', '', FONT_FILE)
    pdf.set_font('NotoSans', '', 10)

    # 4. Process Files
    full_content = ""

    for file_path in txt_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Get a clean header name based on folder structure
                # e.g., "Bases 2015/Subject.txt"
                rel_path = os.path.relpath(file_path, SOURCE_DIR)
                header = f"\n\n{'='*20}\nFILE: {rel_path}\n{'='*20}\n\n"
                
                # Append to TXT buffer
                full_content += header + content
                
                # Add to PDF
                pdf.set_font('NotoSans', '', 12)
                pdf.cell(0, 10, f"FILE: {rel_path}", ln=True)
                pdf.set_font('NotoSans', '', 10)
                pdf.multi_cell(0, 5, clean_text(content))
                pdf.ln(5)
                
                print(f"Processed: {rel_path}")
        except Exception as e:
            print(f"Failed to process {file_path}: {e}")

    # 5. Save TXT
    txt_output_path = os.path.join(OUTPUT_DIR, f"{OUTPUT_FILENAME}.txt")
    with open(txt_output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)
    print(f"Saved TXT: {txt_output_path}")

    # 6. Save PDF
    pdf_output_path = os.path.join(OUTPUT_DIR, f"{OUTPUT_FILENAME}.pdf")
    try:
        pdf.output(pdf_output_path)
        print(f"Saved PDF: {pdf_output_path}")
    except Exception as e:
        print(f"Error saving PDF: {e}")

    # Cleanup font file
    if os.path.exists(FONT_FILE):
        os.remove(FONT_FILE)

if __name__ == "__main__":
    main()
