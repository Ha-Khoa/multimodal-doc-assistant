"""
Test multi-document support:
- ingest 2 PDFs
- query each separately - no data leakage between file
"""

import sys, os
#look at the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#                                 #join with '..' which is the parent file #get the name of the file

from dotenv import load_dotenv
load_dotenv()

from app.ingestion.pdf_parser import parse_pdf
from app.ingestion.chunker import chunk_text, chunk_image_description
from app.ingestion.image_describer import describe_page_image
from app.retrieval.vectorstore import get_vectorstore
from app.chat import build_chain, ask

#2 different files
PDF_A = "sample_docs/career-report-khoa copy.pdf"
PDF_B = "sample_docs/javier-briceno.pdf"

NAME_A = os.path.basename(PDF_A)
NAME_B = os.path.basename(PDF_B)

store = get_vectorstore()

def ingest(pdf_path: str) -> int:
    """
    Parse + chunk + ingest 1 PDF
    Return number of chunks
    """
    pages = parse_pdf(pdf_path)
    all_docs = []
    for page in pages:
        all_docs.extend(chunk_text(page.text, page.source_file, page.page_number))
        desc = describe_page_image(page.image_b64, page.page_number, page.source_file)
        all_docs.extend(chunk_image_description(desc, page.source_file, page.page_number))
    store.add_documents(all_docs)  
    return len(all_docs)

# Step 1: Ingest 2 files
print("Ingesting file A")
n_a = ingest(PDF_A)
print(f"OK - {n_a} chunks from {NAME_A}")

print("Ingesting file B")
n_b = ingest(PDF_B)
print(f"OK - {n_b} chunks from {NAME_B}")

# Step 2: chain for each file 
chain_a = build_chain(source_file=NAME_A)
chain_b = build_chain(source_file=NAME_B)

# Step 3: ask question
question = "What is this person's GPA or academic performance?"

print(f"\n{'─'*50}")
print(f"Q (asked to both chains): {question}")

result_a = ask(chain_a, question, session_id="session_a")
print(f"\nA from PDF A: {result_a['answer']}")
print(f"Sources A: {result_a['sources']}")

result_b = ask(chain_b, question, session_id="session_b")
print(f"\nA from PDF B: {result_b['answer']}")
print(f"Sources B: {result_b['sources']}")

# Step 4: Check for the data leakage
print(f"\n{'─'*50}")
print("Checking data isolation...")

for src in result_a['sources']:
    assert NAME_B not in src, f"FAIL — PDF B data leaked into PDF A answer: {src}"

for src in result_b['sources']:
    assert NAME_A not in src, f"FAIL — PDF A data leaked into PDF B answer: {src}"

print("OK — no data leakage between documents")

