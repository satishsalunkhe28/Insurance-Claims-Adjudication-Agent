from vector_store import load_vector_database


def create_retriever():

    vector_database = load_vector_database()

    retriever = vector_database.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 3
        }
    )

    return retriever


def search_policy(question):

    retriever = create_retriever()

    documents = retriever.invoke(question)

    return documents


if __name__ == "__main__":

    test_question = (
        "My car engine stopped after I drove through flood water. "
        "Is the engine damage covered?"
    )

    print("\nUser Question:")
    print(test_question)

    results = search_policy(test_question)

    print(f"\nRetrieved Documents: {len(results)}")

    for index, document in enumerate(results, start=1):

        print("\n" + "=" * 60)

        print(f"Result {index}")

        print(f"File: {document.metadata.get('file_name')}")

        print(f"Source: {document.metadata.get('source')}")

        print("\nContent:")

        print(document.page_content)