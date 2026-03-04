from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from data_loader import load_all_documents

PERSIST_DIR = "chroma_db_emb2_k15"


def create_vector_store():
    documents = load_all_documents()

   
    embeddings = OllamaEmbeddings(
        model="mxbai-embed-large"
    )

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=PERSIST_DIR
    )

    print("Vector store created successfully!")

    return vector_store

def get_retriever():
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    vector_store = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": 15})

    return retriever


if __name__ == "__main__":
    create_vector_store()
