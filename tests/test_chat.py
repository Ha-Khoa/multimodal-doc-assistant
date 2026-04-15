"""
Test conversational chain - retrieval + memory + answer generation
"""

import sys
import os
#look at the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#                                 #join with '..' which is the parent file #get the name of the file

from dotenv import load_dotenv
load_dotenv()

from app.chat import build_chain, ask

PDF_PATH = "sample_docs/career-report-khoa copy.pdf"
PDF_NAME = "career-report-khoa copy.pdf"

print("Building chain")
chain = build_chain(source_file=PDF_NAME)
print("OK\n")

#Test 1: normal question
q1 = "What is Khoa's GPA?"
print(f"Q: {q1}")
result1 = ask(chain, q1)
print(f"A: {result1['answer']}")
print(f"Sources: {result1['sources']}\n")

#Test 2: follow-up question - test memory
q2 = "What are his strongest subjects?"
print(f"Q: {q2}")
result2 = ask(chain, q2)
print(f"A: {result2['answer']}")
print(f"Sources: {result2['sources']}\n")

#Test 3: Question using context from previous question - test memory
q3 = "Based on those subjects, which career path fits him best?"
print(f"Q: {q3}")
result3 = ask(chain, q3)
print(f"A: {result3['answer']}")
print(f"Sources: {result3['sources']}\n")