"""
Test full ingestion pipeline:
pdf_parser -> chunker -> vectorstore
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from app.ingestion.pdf_parser import parse_pdf
from app.ingestion.chunker import chunk_text, chunk_image_description
from app.retrieval.vectorstore import get_vectorstore, ingest_documents

PDF_PATH = "sample_docs/career-report-khoa copy.pdf"

#Step 1: Parse PDF
print("Step 1: Parsing PDF")
pages = parse_pdf(PDF_PATH)
print(f"OK - {len(pages)} pages parsed")

#Step 2: Chunk
print("\nStep 2: Chunking")
all_docs = []
for page in pages:
    text_chunk = chunk_text(page.text, page.source_file, page.page_number)
    all_docs.extend(text_chunk)
print(f"OK - {len(all_docs)} text chunks created")

#Step 3: Ingest to pgvector
print("\n Ingesting into pgvector")
store = get_vectorstore()
store.add_documents(all_docs)
print(f"OK - {len(all_docs)} chunk embedded and saved")

#Step 4: test query
print("\nTesting similarity search")
results = store.similarity_search("career path recommendation", k = 3)
for i, doc in enumerate(results):
    print(f"\nResult {i+1}")
    print(f"Source: {doc.metadata['source_file']}, page {doc.metadata['page_number']}")
    print(f"Preview: {doc.page_content[:80]!r}")

print("\nAll step passed!")