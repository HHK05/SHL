import json
import numpy as np
from sklearn.metrics import average_precision_score
from app4 import embed_text, recommend_assessments  # Make sure these are imported properly

# 🔧 Benchmark data — mock examples (replace these with your real test cases)
benchmark = [
    {
        "query": "Looking for a software engineer with experience in Python, data structures, and backend systems.",
        "expected_names": ["Cognitive Ability Test", "Programming Fundamentals", "Software Engineer Assessment"]
    },
    {
        "query": "Sales representative with strong interpersonal and persuasion skills.",
        "expected_names": ["Sales Skills Test", "Verbal Reasoning Test", "Personality Questionnaire"]
    },
    {
        "query": "Financial analyst role requiring numerical reasoning and problem solving.",
        "expected_names": ["Numerical Reasoning Test", "Cognitive Ability Test", "Critical Thinking Assessment"]
    }
]

# 📊 Evaluation metrics
def recall_at_k(predicted, actual, k=3):
    return len(set(predicted[:k]) & set(actual)) / len(set(actual))

def apk(actual, predicted, k=3):
    if len(predicted) > k:
        predicted = predicted[:k]

    score = 0.0
    hits = 0.0

    for i, p in enumerate(predicted):
        if p in actual and p not in predicted[:i]:
            hits += 1.0
            score += hits / (i + 1.0)

    return score / min(len(actual), k) if actual else 0.0

# 🧪 Evaluation loop
recalls = []
maps = []

for i, sample in enumerate(benchmark):
    query = sample["query"]
    expected = sample["expected_names"]

    recommendations = recommend_assessments(query, top_k=3)
    predicted_names = [rec["Assessment Name"] for rec in recommendations]

    rec = recall_at_k(predicted_names, expected)
    m = apk(expected, predicted_names)

    recalls.append(rec)
    maps.append(m)

    print(f"\nQuery {i+1}:")
    print("Query Text:", query)
    print("Expected:", expected)
    print("Predicted:", predicted_names)
    print(f"Recall@3: {rec:.3f}, MAP@3: {m:.3f}")

# 📈 Final Results
print("\n========== Overall Evaluation ==========")
print(f"Mean Recall@3: {np.mean(recalls):.3f}")
print(f"Mean MAP@3: {np.mean(maps):.3f}")
