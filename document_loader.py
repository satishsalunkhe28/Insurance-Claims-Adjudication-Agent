from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Project root folder (folder where this Python file exists)
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_FOLDER = PROJECT_ROOT / "data"


def load_documents():
    """
    Load all .txt policy documents recursively from the data folder
    and split them into chunks.
    """

    print("\n" + "=" * 60)
    print("DOCUMENT LOADER STARTED")
    print("=" * 60)
    print(f"Data folder: {DATA_FOLDER}")

    if not DATA_FOLDER.exists():
        raise FileNotFoundError(
            f"Data folder was not found: {DATA_FOLDER}"
        )

    text_files = sorted(DATA_FOLDER.rglob("*.txt"))

    print(f"Text files found: {len(text_files)}")

    for file_path in text_files:
        print(f" - {file_path.relative_to(PROJECT_ROOT)}")

    if not text_files:
        raise FileNotFoundError(
            "No .txt files were found inside the data folder. "
            "Make sure the policy documents are committed to GitHub."
        )

    documents = []

    for file_path in text_files:
        try:
            content = file_path.read_text(
                encoding="utf-8"
            ).strip()
        except UnicodeDecodeError:
            content = file_path.read_text(
                encoding="utf-8",
                errors="ignore"
            ).strip()

        if not content:
            print(
                f"Skipping empty file: "
                f"{file_path.relative_to(PROJECT_ROOT)}"
            )
            continue

        document = Document(
            page_content=content,
            metadata={
                "file_name": file_path.name,
                "source": str(
                    file_path.relative_to(PROJECT_ROOT)
                ),
                "category": file_path.parent.name
            }
        )

        documents.append(document)

    if not documents:
        raise ValueError(
            "Text files were found, but all files were empty."
        )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = text_splitter.split_documents(documents)

    print(f"Documents loaded: {len(documents)}")
    print(f"Chunks created: {len(chunks)}")
    print("=" * 60)

    if not chunks:
        raise ValueError(
            "Documents were loaded, but no chunks were created."
        )

    return chunks


if __name__ == "__main__":
    chunks = load_documents()

    print("\nFirst Chunk:\n")
    print(chunks[0].page_content)