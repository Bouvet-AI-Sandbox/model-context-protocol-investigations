import os
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document

class ContextManager:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma(embedding_function=self.embeddings, persist_directory="./context_db")

    def add_context(self, key, value):
        doc = Document(page_content=value, metadata={"key": key})
        self.vectorstore.add_documents([doc])

    def get_context(self, query):
        results = self.vectorstore.similarity_search(query, k=1)
        return results[0].page_content if results else "No relevant context found."