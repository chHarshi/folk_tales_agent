from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os

class RAGAgent:
    def __init__(self):
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.vectordb = Chroma(
            collection_name="folk_tales",
            embedding_function=self.embedding_model,
            persist_directory="embeddings"
        )

        self.retriever = self.vectordb.as_retriever(search_kwargs={"k": 8})

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7
        )

        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are an Indian folk storyteller.

Using the following folk tale context, narrate a **complete story** in a natural storytelling manner.
If the context is partial, complete the story while staying strictly faithful to the retrieved context.
Always include a moral at the end.

Context:
{context}

User question:
{question}

Story:
"""
        )

    def run(self, query):
        docs = self.retriever.invoke(query)
        context = "\n".join([doc.page_content for doc in docs])

        chain = self.prompt | self.llm
        story = chain.invoke(
            {"context": context, "question": query}
         ).content

        return story, context



