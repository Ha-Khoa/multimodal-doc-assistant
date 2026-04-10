"""
Test with PDF 2-5 pages
"""
import sys
import os
#look at the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#                                 #join with '..' which is the parent file #get the name of the file
from app.ingestion.pdf_parser import parse_pdf

#take the pdf from sample_docs
PDF_PATH = "sample_docs/career-report-khoa copy.pdf"

#extract text from the pdf
pages = parse_pdf(PDF_PATH)

print(f"Total pages: {len(pages)}")

#print all the information for each page
for page in pages:
    print(f"\n---Page {page.page_number}")
    print(f"Source: {page.source_file}")
    print(f"Text length: {len(page.text)} chars")
    print(f"Text preview: {page.text[:80]!r}")
    print(f"Image b64 length: {len(page.image_b64)}")