import fitz 
import base64
from pathlib import Path
from dataclasses import dataclass

@dataclass
class PageData:
    source_file: str
    page_number: int
    text: str
    image_b64: str      #base64-encoded PNG of the full page

def parse_pdf(pdf_path: str, dpi: int = 150) -> list[PageData]:
    """
    Extract text and render each page as an image
    """
    path = Path(pdf_path)
    doc = fitz.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]

        # --- Text extraction ---
        text = page.get_text("text").strip()

        #--- Page --> image (for Vision LLM)---
        mat = fitz.Matrix(dpi/72, dpi/72)   #scale factor
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")

        pages.append(PageData(
            source_file=path.name,
            page_number=page_num + 1,
            text=text,
            image_b64=img_b64,
        ))
    
    doc.close()
    return pages