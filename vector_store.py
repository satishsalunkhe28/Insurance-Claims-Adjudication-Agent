from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from document_loader import load_documents


VECTOR_DB_FOLDER = "vector_db"

COLLECTION_NAME = "insurance_policy_documents"


def create_embedding_model():

    print("Loading embedding model...")

    embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )

    print("Embedding model loaded successfully.")

    return embedding_model


def create_vector_database():

    print("Loading and chunking documents...")

    chunks = load_documents()

    print(f"Total chunks loaded: {len(chunks)}")

    embedding_model = create_embedding_model()

    print("Creating Chroma vector database...")

    vector_database = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        collection_name=COLLECTION_NAME,
        persist_directory=VECTOR_DB_FOLDER
    )

    print("Vector database created successfully.")

    return vector_database


def load_vector_database():

    print("Loading existing vector database...")

    embedding_model = create_embedding_model()

    vector_database = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=VECTOR_DB_FOLDER,
        embedding_function=embedding_model
    )

    print("Vector database loaded successfully.")

    return vector_database


if __name__ == "__main__":

    create_vector_database()

    print("\nAll policy chunks are stored in ChromaDB.")