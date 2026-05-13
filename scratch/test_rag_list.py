from app.rag import rag
import json

print("Fetching all documents...")
try:
    docs = rag.get_all_documents()
    print(f"Found {len(docs)} documents.")
    for i, doc in enumerate(docs[:3]):
        print(f"Doc {i}: {doc.metadata.get('destination')} - {doc.page_content[:50]}...")
except Exception as e:
    print("Error:", e)
