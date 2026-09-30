import json, argparse, shutil, os
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import config


def main(path, reset):
    if reset and os.path.exists(config.PERSIST_DIR):
        shutil.rmtree(config.PERSIST_DIR)   # prevents duplicate chunks on re-runs

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP
    )
    docs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = json.loads(line)
            for i, chunk in enumerate(splitter.split_text(s["text"])):
                docs.append(Document(
                    page_content=f"{s['title']} ({s['region']}). {chunk}",
                    metadata={"story_id": s["id"], "title": s["title"],
                              "region": s["region"], "source": s["source"], "chunk_idx": i},
                ))

    print(f"Embedding {len(docs)} chunks (first run downloads the model, so this can take a few minutes)...")
    Chroma.from_documents(
        docs,
        HuggingFaceEmbeddings(model_name=config.EMBED_MODEL),
        collection_name=config.COLLECTION,
        persist_directory=config.PERSIST_DIR,
        collection_metadata={"hnsw:space": "cosine"},
    )
    print(f"Ingested {len(docs)} chunks from {path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default=config.STORIES_PATH)
    p.add_argument("--reset", action="store_true")
    a = p.parse_args()
    main(a.data, a.reset)