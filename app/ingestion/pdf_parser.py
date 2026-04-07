"""
Convert PDF to data for processing.
"""

import fitz                         # PyMuPDF - read and render PDF
import base64                       # encode image to text and send to API
from pathlib import Path            # process the file's directory
from dataclasses import dataclass   # create better data container

@dataclass                          #auto-generates __init__, __repr__ from field definitions
class PageData:
    source_file: str
    page_number: int
    text: str
    image_b64: str      #base64-encoded PNG of the full page

# Having the directory path to pdf, return a list (PageData) of a page, resolution while rendering 150 
def parse_pdf(pdf_path: str, dpi: int = 150) -> list[PageData]:     
    """
    Extract text and render each page as an image
    Returns one PageData per page
    """    

    path = Path(pdf_path)                   #path of the pdf
    doc = fitz.open(pdf_path)               # open the PDF file, load into memory
    pages = []                              #list of the results, each index is a page

    # loop for each page, to get the extraction
    # doc[i]: page number i
    # page is object for a page
    for page_num in range(len(doc)):
        page = doc[page_num]

        # --- text extraction ---
        # strip(): remove leading/trailing whitespaces in the text 
        text = page.get_text("text").strip()                
        # this text can't be seen --> we use the page -> image

        #--- page --> image (for Vision LLM)---
        mat = fitz.Matrix(dpi/72, dpi/72)                               #scale factor: 72 points/inch: official unit for pdf printing
        pix = page.get_pixmap(matrix=mat)                               #render page: raw pixel (RGB)
        img_bytes = pix.tobytes("png")                                  #compress pixel --> PNG binary
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")           #binary --> text safe for JSON 

        pages.append(PageData(
            source_file=path.name,                                      #take only the name, not full path. Later used as metadata source_file
            page_number=page_num + 1,                                   #page_num starts with 0, so we add 1
            text=text,                                                  
            image_b64=img_b64,
        ))
    
    doc.close()                                                         #release memory
    return pages