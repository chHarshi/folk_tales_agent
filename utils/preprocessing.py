from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os

def load_and_chunk_txt(folder_path):
    documents = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                text = f.read()
                documents.append(Document(page_content=text))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    return splitter.split_documents(documents)

