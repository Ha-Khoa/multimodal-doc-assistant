"""
Conversational chain - retrieval +  memory + answer generation
"""
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from app.retrieval.vectorstore import get_vectorstore

llm = ChatOpenAI(model="gpt-4o", temperature=0)

#store sessions in memory (dict)
session_store: dict[str, BaseChatMessageHistory] = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Return chat history for a session, create if not exists
    """
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]

def build_chain(source_file: str | None = None, subject: str | None = None):
    """
    Build a conversational retrieval chain
    If source_file given, filter chunks to that file only
    """
    store = get_vectorstore()

    search_kwargs = {"k": 5}
    if source_file and subject:
        search_kwargs["filter"] = {
            "$and": [
                {"source_file": {"$eq":source_file}},
                {"subject": {"$eq": subject}}
            ]
        }
    elif source_file:
        search_kwargs["filter"] = {"source_file": {"$eq":source_file}}
    elif subject:
        search_kwargs["filter"] = {"subject": {"$eq": subject}}
    
    retriever = store.as_retriever(search_kwargs = search_kwargs)

    # PGVector JSONB filter format: {"key": {"$eq": value}}
    #    search_kwargs["filter"] = {"source_file": {"$eq": source_file}}

    #Step 1: rewrite user question using chat history
    # so follow-up questions work correctly
    contextualize_prompt = ChatPromptTemplate.from_messages([
        ("system", "Given chat history and the latest user question, "
                    "rewrite it as a standalone question."
                    "Do NOT answer it, just rewrite if needed"),
        MessagesPlaceholder("chat_history"),
        ("human","{input}"),
    ])
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_prompt)

    #Step 2: answer using retrieved chunks
    answer_promt = ChatPromptTemplate.from_messages([
        ("system", "You are a document assistant. Answer using only the context below. \n\n"
                    "Context: \n{context}"),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    question_answer_chain = create_stuff_documents_chain(llm, answer_promt)

    #Step 3: combine retriever + answer chain
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    #Step 4: wrap with message history
    chain_with_history = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    return chain_with_history

def ask(chain, question: str, session_id: str = "default") -> dict:
    """
    Invoke chain, return answer + source citations
    """
    result = chain.invoke(
        {"input": question},
        config={"configurable": {"session_id": session_id}},
    )

    sources = [
        f"{doc.metadata.get('source_file')},"
        f"page {doc.metadata.get('page_number')} "
        f"[{doc.metadata.get('chunk_type')}]"
        for doc in result.get("context", [])
    ]

    return {
        "answer": result["answer"],
        "sources": list(dict.fromkeys(sources)),            #deduplicate
    }