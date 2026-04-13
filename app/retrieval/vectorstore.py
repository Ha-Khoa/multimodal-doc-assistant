"""
pgVector setup using LangChain's PGVector integration
"""
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

COLLECTION_NAME = "doc_chunks"

# Debug: check if API key is loaded
#api_key = os.environ.get('OPENAI_API_KEY', 'NOT_FOUND')
#print(f"DEBUG: API Key loaded: {api_key[:20]}..." if api_key != 'NOT_FOUND' else "DEBUG: API Key NOT FOUND")

"""
Connect to the PostgreSQL
"""
CONNECTION_STRING = (
    f"postgresql+psycopg://{os.environ['POSTGRES_USER']}:"
    f"{os.environ['POSTGRES_PASSWORD']}@"
    f"{os.environ['POSTGRES_HOST']}:"
    f"{os.environ['POSTGRES_PORT']}/"
    f"{os.environ['POSTGRES_DB']}"
)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")       #return vector 1536 dimensions

def get_vectorstore() -> PGVector:                      #return PGVector object for working with vector DB
    return PGVector(
        embeddings = embeddings,                        # using this embed model we gave it
        collection_name = COLLECTION_NAME,              # save to this collection (table)
        connection = CONNECTION_STRING,                 # connect to this database. 
        use_jsonb=True,                                 #metadata of each chunks(source_file, page_number, chunk_type) is saved as JSONB in PostgreSQL
    )


def ingest_documents(docs: list[Document]) -> None:
    """
    Add document to pgvector
    Received a list `Document` and save in DB
    """
    store = get_vectorstore()                           #return a PGVector Object knowing which embed model to use
    #How .add_documents work
    #1. take a list of Document object
    #2. call OpenAI, using the object above in the get_vectorstore() and convert into embedding.  --> "learn Python ..." -> [0.324, 0.324, 0.23423,...] (1536 number)
    #3. store data so they can be retrieved: INSERT INTO doc_chunks(content, embedding) VALUES(...)
    store.add_documents(docs)                           
    print(f"Ingested {len(docs)} chunks into pgvector")