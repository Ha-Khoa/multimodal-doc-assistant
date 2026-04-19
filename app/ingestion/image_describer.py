"""
Send each page image to GPT-4o Vision and get a text description
"""
from openai import OpenAI
import os

#a client connect to OpenAI with API KEY
client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])

VISION_PROMPT = """You are a document analyst. Describe this page in detail:
- All text content (transcribe key passages)
- Any charts or graphs (describe axes, values, trends)
- Any tables (describes columns, key rows, notable values)
- Any diagrams or figures (describe what they show)

Be specifics with numbers and labels. This description will be used
to answer questions about the document."""

SLIDE_VISION_PROMPT ="""You are a lecture slide analyst. Describe this slide in detail:
- The slide title and main topic
- All text content and bullet points (transcribe completely)
- Any diagrams, flowcharts or figures (describe what they show and how elements connect)
- Any code snippets (transcribe exactly)
- Any formulas or equations (describe precisely)
- Any tables (describe columns and values)

Be thorough - this description will be used to answer exam questions about the slide."""

# receive image in base64 string (from pdf_parser.pdf.py), page_number and source file
#return a description string
def describe_page_image(image_b64: str, page_number: int, source_file: str) -> str:
    """
    Send a page image  to GPT-4o Vision
    Return  a detailed text description of the page
    """

    # using chatgpt with model 4o
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            #user can send message with content (image_url and text)
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_b64}",
                        "detail": "high"
                    }
                },
                {
                    "type": "text",
                    "text": VISION_PROMPT
                }
            ]
        }],
        max_tokens=1000,            #maximum 750 words
    )
    #message.content is the text, which is sent by ChatGPT 4o, we will pass in chunk_image_description()
    return response.choices[0].message.content	        

def describe_slide_image(image_b64: str, page_number: int, source_file: str) -> str:
    """
    send a slide image to GPT-4o Vision
    uses a more detailed prompt optimized for lecture slides.
    """
    print(f"Describing {source_file} slide {page_number}")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64, {image_b64}",
                        "detail": "high"
                    }
                },
                {
                    "type": "text",
                    "text": SLIDE_VISION_PROMPT
                }
            ]
        }],
        max_tokens=1500,
    )
    return response.choices[0].message.content