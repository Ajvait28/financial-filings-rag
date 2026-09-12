import os
from bs4 import BeautifulSoup

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

def clean_html_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ")

    marker = "UNITED STATES SECURITIES AND EXCHANGE COMMISSION"
    if marker in text:
        text = text[text.index(marker):]

    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    cleaned = "\n".join(lines)

    return cleaned

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