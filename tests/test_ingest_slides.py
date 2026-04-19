"""
Ingest lecture slides into pgvector
"""

import sys
import os
#look at the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#                                 #join with '..' which is the parent file #get the name of the file

from dotenv import load_dotenv
load_dotenv()

from app.ingestion.pdf_parser import parse_pdf
from app.ingestion.chunker import chunk_text_slides, chunk_image_description
from app.ingestion.image_describer import describe_slide_image
from app.retrieval.vectorstore import get_vectorstore

SLIDES = [
    {"path": "sample_docs/ciss-IS-02-ml-1 (knn).pdf", "subject": "Machine Learning"},
    {"path": "sample_docs/5_map_filter_reduce_wrapup.pdf",   "subject": "OOP"},
]

store = get_vectorstore()

for slide_info in SLIDES:
    path = slide_info["path"]
    subject = slide_info["subject"]
    name = os.path.basename(path)

    print(f"\nIngesting: {name} [{subject}]")
    pages = parse_pdf(path, dpi=200)
    all_docs = []

    for page in pages:
        #smaller chunk for slide
        text_chunks = chunk_text_slides(page.text, page.source_file, page.page_number, subject)
        all_docs.extend(text_chunks)

        #image description with prompt 
        desc = describe_slide_image(page.image_b64, page.page_number, page.source_file)
        image_chunks = chunk_image_description(desc, page.source_file, page.page_number)
        image_chunks[0].metadata["subject"] = subject
        image_chunks[0].metadata["doc_type"] = "slide"
        all_docs.extend(image_chunks)

        print(f"Slide {page.page_number}: {len(text_chunks)} text + 1 image chunk")
    
    store.add_documents(all_docs)
    print(f"OK - {len(all_docs)} chunks from {name}")

# Thêm vào test_ingest_slides.py sau khi ingest xong
store = get_vectorstore()
results = store.similarity_search(
    "scatter plot salary classification",
    k=3,
    filter={"source_file": {"$eq": "ciss-IS-02-ml-1 (knn).pdf"}}
)
for r in results:
    print(r.metadata['chunk_type'], r.page_content[:100])