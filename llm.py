import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


# Load environment variables from the .env file
load_dotenv()


def create_llm():
    """
    Create and return the Groq LLM.

    This LLM will later read the retrieved insurance policy
    documents and analyze whether a claim is covered.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY was not found. "
            "Please add it to your .env file."
        )

    llm = ChatGroq(
        groq_api_key=api_key,
        model="llama-3.3-70b-versatile",
        temperature=0
    )

    return llm


# This section runs only when we execute:
# python llm.py
if __name__ == "__main__":

    try:
        print("Loading Groq LLM...")

        llm = create_llm()

        print("Groq LLM loaded successfully.")

        response = llm.invoke(
            "Say hello in one short sentence."
        )

        print("\nLLM Response:")
        print(response.content)

    except Exception as error:
        print("\nError:")
        print(error)