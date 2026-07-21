import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from document_loader import load_documents


PROJECT_ROOT = Path(__file__).resolve().parent
VECTOR_DB_FOLDER = PROJECT_ROOT / "vector_db"
COLLECTION_NAME = "insurance_policy_documents"


def create_embedding_model():
    """
    Create the Hugging Face embedding model.
    """

    print("\nLoading embedding model...")

    embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        }
    )

    print("Embedding model loaded successfully.")

    return embedding_model


def create_vector_database(
    embedding_model=None
):
    """
    Create a new Chroma vector database from the text documents.
    """

    print("\nCreating vector database...")

    chunks = load_documents()

    if not chunks:
        raise ValueError(
            "No document chunks are available for indexing."
        )

    if embedding_model is None:
        embedding_model = create_embedding_model()

    VECTOR_DB_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    vector_database = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        collection_name=COLLECTION_NAME,
        persist_directory=str(VECTOR_DB_FOLDER)
    )

    stored_count = vector_database._collection.count()

    print(
        f"Vector database created successfully. "
        f"Stored chunks: {stored_count}"
    )

    if stored_count == 0:
        raise RuntimeError(
            "The vector database was created, "
            "but it contains zero chunks."
        )

    return vector_database


def load_vector_database():
    """
    Load the existing Chroma database.

    If the database is missing, damaged, or empty,
    automatically rebuild it from the text documents.
    """

    embedding_model = create_embedding_model()

    database_file = (
        VECTOR_DB_FOLDER / "chroma.sqlite3"
    )

    if not database_file.exists():
        print(
            "\nVector database was not found. "
            "Creating it automatically..."
        )

        return create_vector_database(
            embedding_model=embedding_model
        )

    try:
        print("\nLoading existing vector database...")

        vector_database = Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=str(VECTOR_DB_FOLDER),
            embedding_function=embedding_model
        )

        stored_count = (
            vector_database._collection.count()
        )

        print(
            f"Existing vector database chunks: "
            f"{stored_count}"
        )

        if stored_count == 0:
            raise ValueError(
                "Existing vector database is empty."
            )

        print(
            "Vector database loaded successfully."
        )

        return vector_database

    except Exception as error:
        print(
            "\nExisting vector database could not "
            "be used."
        )
        print(f"Reason: {error}")
        print("Rebuilding vector database...")

        if VECTOR_DB_FOLDER.exists():
            shutil.rmtree(
                VECTOR_DB_FOLDER,
                ignore_errors=True
            )

        return create_vector_database(
            embedding_model=embedding_model
        )


if __name__ == "__main__":
    database = load_vector_database()

    print(
        "\nAll policy chunks are ready in ChromaDB."
    )
    print(
        f"Total stored chunks: "
        f"{database._collection.count()}"
    )