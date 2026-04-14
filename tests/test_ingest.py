"""
Test full ingestion pipeline:
pdf_parser -> chunker.py + image_describer..py -> vectorstore
"""

import sys
import os
#look at the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#                                 #join with '..' which is the parent file #get the name of the file

#load .env in os.environ before import anything
from dotenv import load_dotenv
load_dotenv()

from app.ingestion.pdf_parser import parse_pdf
from app.ingestion.chunker import chunk_text, chunk_image_description
from app.retrieval.vectorstore import get_vectorstore, ingest_documents
from app.ingestion.image_describer import describe_page_image

#take the pdf from sample_docs
PDF_PATH = "sample_docs/career-report-khoa copy.pdf"

#Step 1: Parse PDF
print("Step 1: Parsing PDF")
pages = parse_pdf(PDF_PATH)
print(f"OK - {len(pages)} pages parsed")

#Step 2: Chunk
print("\nStep 2: Chunking text + describing image with GPT-4o Vision")
all_docs = []
for page in pages:
    #text chunk
    text_chunks = chunk_text(page.text, page.source_file, page.page_number)
    all_docs.extend(text_chunks)

    #image describer chunk 
    description = describe_page_image(page.image_b64, page.page_number, page.source_file)
    image_chunks = chunk_image_description(description, page.source_file, page.page_number)
    all_docs.extend(image_chunks) 

    print(f"  Page {page.page_number}: {len(text_chunks)} text chunks + 1 image chunk")
print(f"OK - {len(all_docs)} text chunks created")

#Step 3: Ingest to pgvector
print("\n Ingesting into pgvector")
store = get_vectorstore()
store.add_documents(all_docs)
print(f"OK - {len(all_docs)} chunk embedded and saved")

#Step 4: test query
print("\nTesting similarity search")
#results = store.similarity_search("career path recommendation", k = 3)
results = store.similarity_search("what courses should Khoa pay for?", k=3)
for i, doc in enumerate(results):
    print(f"\nResult {i+1} [{doc.metadata['chunk_type']}]:")
    print(f"Source: {doc.metadata['source_file']}, page {doc.metadata['page_number']}")
    print(f"Preview: {doc.page_content[:120]!r}")

print("\nAll step passed!")