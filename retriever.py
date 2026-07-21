from functools import lru_cache

from vector_store import load_vector_database


@lru_cache(maxsize=1)
def get_vector_database():
    """
    Load the vector database once per application process.
    """

    return load_vector_database()


def create_retriever():
    """
    Create the policy document retriever.
    """

    vector_database = get_vector_database()

    retriever = vector_database.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 4
        }
    )

    return retriever


def search_policy(question):
    """
    Search the insurance policy knowledge base.
    """

    if not question or not question.strip():
        return []

    print("\n" + "=" * 60)
    print("POLICY RETRIEVAL STARTED")
    print("=" * 60)
    print(f"Search query: {question}")

    retriever = create_retriever()

    documents = retriever.invoke(
        question.strip()
    )

    print(
        f"Documents retrieved: {len(documents)}"
    )

    for index, document in enumerate(
        documents,
        start=1
    ):
        print(
            f"{index}. "
            f"{document.metadata.get('file_name', 'Unknown')}"
        )

    print("=" * 60)

    return documents


if __name__ == "__main__":
    test_question = (
        "My car engine stopped after I drove "
        "through flood water. Is the engine "
        "damage covered?"
    )

    results = search_policy(test_question)

    print(f"\nRetrieved Documents: {len(results)}")

    for index, document in enumerate(
        results,
        start=1
    ):
        print("\n" + "=" * 60)
        print(f"Result {index}")
        print(
            f"File: "
            f"{document.metadata.get('file_name')}"
        )
        print(
            f"Source: "
            f"{document.metadata.get('source')}"
        )
        print("\nContent:")
        print(document.page_content)