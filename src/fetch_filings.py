import requests
from bs4 import BeautifulSoup
import os
import time

HEADERS = {
    "User-Agent": "Adomas Vaitkus (avaitkus@mit.edu)"
}

APPLE_CIK = "0000320193"

def get_filing_list(cik):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_filing_documents(cik, accession):
    cik_no_zeros = str(int(cik))
    accession_no_dashes = accession.replace("-", "")
    index_url = f"https://www.sec.gov/Archives/edgar/data/{cik_no_zeros}/{accession_no_dashes}/{accession}-index.htm"

    response = requests.get(index_url, headers=HEADERS)
    response.raise_for_status()
    return response.text

def get_10q_document_url(cik, accession):
    cik_no_zeros = str(int(cik))
    accession_no_dashes = accession.replace("-", "")
    index_html = get_filing_documents(cik, accession)

    soup = BeautifulSoup(index_html, "html.parser")
    table = soup.find("table", class_="tableFile")

    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 4:
            continue
        doc_type = cells[3].text.strip()
        if doc_type == "10-Q":
            link_tag = cells[2].find("a")
            filename = link_tag.text.strip()
            doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_no_zeros}/{accession_no_dashes}/{filename}"
            return doc_url

    return None

if __name__ == "__main__":
    data = get_filing_list(APPLE_CIK)
    recent = data["filings"]["recent"]

    ten_qs = []
    for form, date, accession in zip(recent["form"], recent["filingDate"], recent["accessionNumber"]):
        if form == "10-Q":
            ten_qs.append((date, accession))

    target_filings = ten_qs[:4]

    os.makedirs("data/raw", exist_ok=True)

    for date, accession in target_filings:
        print(f"Processing {date} ({accession})...")
        doc_url = get_10q_document_url(APPLE_CIK, accession)

        response = requests.get(doc_url, headers=HEADERS)
        response.raise_for_status()

        filename = f"data/raw/aapl_10q_{date}.htm"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)

        print(f"Saved to {filename}")
        time.sleep(1)