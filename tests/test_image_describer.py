"""
Test GPT-4o Vision on 1 page of PDF.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()               #load .env in os.environ before import anything

from app.ingestion.pdf_parser import parse_pdf
from app.ingestion.image_describer import describe_page_image

PDF_PATH = "sample_docs/career-report-khoa copy.pdf"

# Test only one page for saving money
print("Parsing PDF")
pages = parse_pdf(PDF_PATH)
page = pages[0]   # take the first page
print(f"OK — testing Vision on page {page.page_number}")

print("\nSending to GPT-4o Vision")
description = describe_page_image(
    image_b64=page.image_b64,
    page_number=page.page_number,
    source_file=page.source_file
)

print(f"\nDescription ({len(description)} chars):")
print(description)