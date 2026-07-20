from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_documents():

    data_folder = Path("data")

    text_files = list(data_folder.rglob("*.txt"))

    documents = []

    for file in text_files:

        content = file.read_text(encoding="utf-8")

        document = Document(
            page_content=content,
            metadata={
                "file_name": file.name,
                "source": str(file)
            }
        )

        documents.append(document)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = text_splitter.split_documents(documents)

    return chunks


# Run only when this file is executed directly
if __name__ == "__main__":

    chunks = load_documents()

    print(f"Chunks Created : {len(chunks)}")

    print("\nFirst Chunk:\n")

    print(chunks[0].page_content)