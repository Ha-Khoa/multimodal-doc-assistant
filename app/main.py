"""
Streamlit UI - upload PDF, chat with it
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import tempfile
from dotenv import load_dotenv
load_dotenv()

from app.ingestion.pdf_parser import parse_pdf
from app.ingestion.image_describer import describe_page_image
from app.ingestion.chunker import chunk_text, chunk_image_description, chunk_text_slides
from app.retrieval.vectorstore import get_vectorstore
from app.chat import build_chain, ask

st.set_page_config(page_title="Document Assistant", layout="wide")
st.title("Multimodal Document Assistant")
st.caption("Upload a PDF - I understand text, charts, tables and diagrams.")

#----sidebar-----
with st.sidebar:
    st.header("Upload Document")
    doc_type = st.radio("Document Type", ["Report", "Lecture Slide"])
    uploaded = st.file_uploader("Choose a PDF", type=["pdf"])

    if uploaded and st.button("Process Document"):
        with st.spinner("Parsing and indexing..."):
            #save to temp_file, parse need a real path
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name
            
            pages = parse_pdf(tmp_path)
            all_docs = []

            progress = st.progress(0)
            for i, page in enumerate(pages):
                #use different chunk size base on the type of document
                if doc_type == "Lecture Slide":
                    all_docs.extend(chunk_text_slides(page.text, uploaded.name, page.page_number, subject="General"))
                else:
                    all_docs.extend(chunk_text(page.text, uploaded.name, page.page_number))
                
                desc = describe_page_image(page.image_b64, page.page_number, uploaded.name)
                all_docs.extend(chunk_image_description(desc, uploaded.name, page.page_number))
                progress.progress((i+1)/len(pages))

            #ingest into pgvector
            store = get_vectorstore()
            store.add_documents(all_docs)
            os.unlink(tmp_path)

            #track all the uploaded files
            if "uploaded_files" not in st.session_state:
                st.session_state["uploaded_files"] = []
            if uploaded.name not in st.session_state["uploaded_files"]:
                st.session_state["uploaded_files"].append(uploaded.name)

            # init history for new file if not exists
            if "all_messages" not in st.session_state:
                st.session_state["all_messages"] = {}
            st.session_state["all_messages"].setdefault(uploaded.name, [])

            #save the document and rebuild chain for this file
            st.session_state["active_doc"] = uploaded.name
            st.session_state["chain"] = build_chain(source_file=uploaded.name)
            #st.session_state["messages"] = []   #reset for new document
            st.success(f"Index {len(all_docs)} chunks from {len(pages)} pages.")

    #dropdown to choose session
    if st.session_state.get("uploaded_files"):
        selected = st.selectbox(
            "Chat with document:",
            st.session_state["uploaded_files"]
        )
        # if user changes file -> rebuild chain + reset chat
        if selected != st.session_state.get("active_doc"):
            st.session_state["active_doc"] = selected
            st.session_state["chain"] = build_chain(source_file=selected)
            #st.session_state["messages"] = []
            st.rerun()
    #show active document
    if "active_doc" in st.session_state:
        st.info(f"Active: {st.session_state['active_doc']}")

#---Build chain if not exist---
if "chain" not in st.session_state:
    st.session_state["chain"] = build_chain(
        source_file=st.session_state.get("active_doc")
    )

#Get massage for active chat
if "all_messages" not in st.session_state:
    st.session_state["all_messages"] = {}

active = st.session_state.get("active_doc", "default")
messages = st.session_state["all_messages"].setdefault(active, []) 

# --- Chat interface---
for msg in messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("Sources"):
                for s in msg["sources"]:
                    st.caption(s)

if prompt := st.chat_input("Ask something about the document..."):
    # add user message
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # get answer
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = ask(
                st.session_state["chain"],
                prompt,
                session_id=f"streamlit_{active}"   # unique session per file
            )
        st.write(result["answer"])
        if result["sources"]:
            with st.expander("Sources"):
                for s in result["sources"]:
                    st.caption(s)

    # save assistant message
    messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"],
    })
