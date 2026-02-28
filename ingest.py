from utils.preprocessing import load_and_chunk_txt
from agents.rag_agent import RAGAgent

DATA_PATH = "data/indian_folk_tales_dataset"

def ingest():
    print("📥 Loading and chunking TXT folk tales...")
    chunks = load_and_chunk_txt(DATA_PATH)

    print(f"🧩 Total chunks created: {len(chunks)}")

    rag = RAGAgent()
    rag.vectordb.add_documents(chunks)

    print("✅ Vector database created successfully!")

if __name__ == "__main__":
    ingest()
