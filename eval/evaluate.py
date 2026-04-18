"""
Evaluation: run 20 questions, measure accuracy.
A answer is correct if the expected keyword appears in the answer.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

import json
from app.chat import build_chain, ask

# Load questions
with open("eval/questions.json") as f:
    questions = json.load(f)

# Build one chain per unique source file
chains = {}
for q in questions:
    name = q["source_file"]
    if name not in chains:
        chains[name] = build_chain(source_file=name)

# Run evaluation
correct = 0
total = len(questions)
results = []

print(f"Running {total} questions...\n")

for i, q in enumerate(questions):
    chain = chains[q["source_file"]]
    session_id = f"eval_{i}"

    result = ask(chain, q["question"], session_id=session_id)
    answer = result["answer"].lower()
    expected = q["expected"].lower()

    is_correct = expected in answer
    if is_correct:
        correct += 1

    results.append({
        "question": q["question"],
        "expected": q["expected"],
        "answer": result["answer"],
        "correct": is_correct,
        "sources": result["sources"],
    })

    status = "PASS" if is_correct else "FAIL"
    print(f"[{status}] Q{i+1}: {q['question']}")
    if not is_correct:
        print(f"       Expected: {q['expected']}")
        print(f"       Got:      {result['answer'][:100]}")

# Summary
accuracy = correct / total * 100
print(f"\n{'─'*50}")
print(f"Accuracy: {correct}/{total} = {accuracy:.1f}%")

# Save results
with open("eval/results.json", "w") as f:
    json.dump({"accuracy": accuracy, "results": results}, f, indent=2)
print("Results saved to eval/results.json")