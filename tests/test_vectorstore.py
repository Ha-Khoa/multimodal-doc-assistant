"""
Test vectorstore
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from app.retrieval.vectorstore import get_vectorstore
from langchain_core.documents import Document

# 1.test if the vectorstore is connected
print("Testing connection...")
store = get_vectorstore()
print("OK -connected to pgvector")

# 2. test with a fake-chunk
test_docs = Document(
    page_content = "Hello Hello, my name is Khoa, this is the project 'multimodal-doc-assistant', help us to read all the PDF",
    metadata = {
        "source_file": "test.pdf",
        "page_number": 1,
        "chunk_type": "text"
    }
)
    
store.add_documents([test_docs])
print("OK - the chunk is embedded and saved")

# 3. test with query
print("\nTesting with similarity search...")
result= store.similarity_search("project", k=1)
print(f"OK - found: '{result[0].page_content}'")