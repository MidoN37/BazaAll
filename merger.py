import os
import requests
import re
from fpdf import FPDF

# --- CONFIGURATION ---
# Paths relative to the repository root
SOURCE_DIR = os.path.join("Українська", "Крок Б", "Лабораторна діагностика")
OUTPUT_DIR = os.path.join("Українська", "Крок Б")
OUTPUT_FILENAME = "Merged_Lab_Diagnostics"
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/notosans/NotoSans-Regular.ttf"
FONT_FILE = "NotoSans-Regular.ttf"

def download_font():
    if not os.path.exists(FONT_FILE):
        print("Downloading font...")
        r = requests.get(FONT_URL)
        with open(FONT_FILE, 'wb') as f:
            f.write(r.content)

def clean_text(text):
    # Normalize characters for PDF
    return text.replace('\u2013', '-').replace('\u2014', '-').replace('\u2019', "'")

def extract_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by "Newline + Number + Dot + Space"
    raw_blocks = re.split(r'\n(?=\d+\.\s)', "\n" + content)
    
    questions = []
    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue
        
        # Remove the leading number to store just the content
        match = re.match(r'\d+\.\s+(.*)', block, re.DOTALL)
        if match:
            questions.append(match.group(1))
            
    return questions

def main():
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory not found: {SOURCE_DIR}")
        print(f"Current working directory: {os.getcwd()}")
        print("Available folders:", os.listdir())
        return
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    txt_files = []
    for root, dirs, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(os.path.join(root, file))
    
    txt_files.sort()
    
    if not txt_files:
        print("No .txt files found.")
        return

    print(f"Processing {len(txt_files)} files...")

    seen_questions = set()
    unique_questions = []

    for file_path in txt_files:
        questions = extract_questions(file_path)
        for q_text in questions:
            # Use first line as unique key
            question_body = q_text.split('\n')[0].strip()
            
            if question_body not in seen_questions:
                seen_questions.add(question_body)
                unique_questions.append(q_text)

    print(f"Total unique questions found: {len(unique_questions)}")

    download_font()
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('NotoSans', '', FONT_FILE)
    pdf.set_font('NotoSans', '', 10)

    full_txt_content = ""

    # Title
    pdf.set_font('NotoSans', '', 16)
    pdf.cell(0, 10, f"Merged Database: {len(unique_questions)} Questions", ln=True, align='C')
    pdf.ln(10)

    for index, q_content in enumerate(unique_questions, 1):
        formatted_block = f"{index}. {q_content}\n\n"
        full_txt_content += formatted_block
        
        # PDF Formatting
        pdf.set_font('NotoSans', '', 11)
        lines = q_content.split('\n')
        question_body = lines[0]
        options = lines[1:]
        
        pdf.multi_cell(0, 6, clean_text(f"{index}. {question_body}"))
        
        pdf.set_font('NotoSans', '', 10)
        for opt in options:
            pdf.multi_cell(0, 5, clean_text(opt))
        
        pdf.ln(4)

    # Save TXT
    txt_out = os.path.join(OUTPUT_DIR, f"{OUTPUT_FILENAME}.txt")
    with open(txt_out, 'w', encoding='utf-8') as f:
        f.write(full_txt_content)
    print(f"Generated TXT: {txt_out}")

    # Save PDF
    pdf_out = os.path.join(OUTPUT_DIR, f"{OUTPUT_FILENAME}.pdf")
    try:
        pdf.output(pdf_out)
        print(f"Generated PDF: {pdf_out}")
    except Exception as e:
        print(f"Error saving PDF: {e}")

    if os.path.exists(FONT_FILE):
        os.remove(FONT_FILE)

if __name__ == "__main__":
    main()
