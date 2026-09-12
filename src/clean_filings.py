"""
Converts raw SEC filing HTML (from data/raw/) into clean plain text
(saved to data/processed/), so the text is usable for chunking and
embedding later.

Raw EDGAR filings contain a lot of content we don't want: <script> and
<style> tags, and a block of machine-readable XBRL metadata (tag names,
dates) that EDGAR embeds before the actual human-readable filing begins.
This script strips both, keeping only the real filing text.
"""

import os
from bs4 import BeautifulSoup

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

#Loads one raw HTML filing, strips non-content tags and the XBRL metadata block, and returns clean, readable plain text.
def clean_html_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    #Scripts and styles aren't real content so remove them before extracting text, or their contents get mixed into the output
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ")

    #Every 10-Q filing has a block of XBRL tags (dates, financial concept identifiers) before the actual filing text starts.
    #This phrase reliably marks where the real, human-readable content begins, so we cut everything before it
    marker = "UNITED STATES SECURITIES AND EXCHANGE COMMISSION"
    if marker in text:
        text = text[text.index(marker):]

    #get_text() leaves a lot of blank lines and stray whitespace behind once tags are stripped and we clean that up so the output reads as normal paragraphs instead of a messy wall of text
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    cleaned = "\n".join(lines)

    return cleaned

#Cleans every raw .htm filing in data/raw/ and writes a matching .txt version to data/processed/, ready for chunking.
if __name__ == "__main__":
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    for filename in os.listdir(RAW_DIR):
        if not filename.endswith(".htm"):
            continue

        raw_path = os.path.join(RAW_DIR, filename)
        cleaned_text = clean_html_file(raw_path)

        out_filename = filename.replace(".htm", ".txt")
        out_path = os.path.join(PROCESSED_DIR, out_filename)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        print(f"Cleaned {filename} -> {out_path}")