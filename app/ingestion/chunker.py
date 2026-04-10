"""
Split page_content into overlapping chunks 
and wrap each chunk as a LangChain Document with source metadata
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter                     #tool for spliting the text into smaller chunk
from langchain_core.documents import Document

#Parameter for the way we split into chunks
CHUNK_SIZE = 1000                       #each chunk has maximum 1000 characters
CHUNK_OVERLAP = 150                     #150 last characters of the previous chunk will appear in the next chunk ---> for protecting the context

def chunk_text(text:str, source_file: str, page_number: int) -> list[Document]:
    """
    split text from pdf_parser into chunk, tagging each other with metadata, 
    return list Document
    """

    #split by the priority 
    # paragraph: (\n\n) first, then line: (\n), sentences: (.) -> words: ( ) -> characters
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = CHUNK_SIZE,
        chunk_overlap = CHUNK_OVERLAP,
    )
    # split the text -> return a list of strings (3000 characters into 4 chunks, each has roughly 1000 characters)
    chunks = splitter.split_text(text)         

    # for each chunk strings, wrap it into a Document with metadata.
    return [
        Document(
            page_content=chunk,
            metadata={  
                "source_file": source_file,
                "page_number": page_number,
                "chunk_type": "text",
            }
        )
        for chunk in chunks if chunk.strip()            # chunk.strip() remove empty chunk or chunk with only whitespace
    ]

def chunk_image_description(description: str, source_file: str, page_number:int) -> list[Document]:
    """Wrap a Vision LLM page description in a single chunk"""
    #image description are usually <1000 tokens - no needs to split further

    #GPT-4o Vision describe 1 page of image, without split further, wrap into a document, return a list
    return [
        Document(
            page_content=description,
            metadata={
                "source_file": source_file,
                "page_number": page_number,
                "chunk_type": "image",                  #type of chunk
            }
        )
    ]
