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
