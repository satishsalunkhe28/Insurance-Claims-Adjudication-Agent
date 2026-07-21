import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


# Load local environment variables from .env
load_dotenv()


def get_groq_api_key():
    """
    Read the Groq API key.

    Priority:
    1. Streamlit Cloud secrets
    2. Local .env or system environment variable
    """

    api_key = None

    # Try Streamlit Cloud secrets
    try:
        import streamlit as st

        if "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]

    except Exception:
        # Streamlit may not be installed or the app may run outside Streamlit
        pass

    # Try local .env or operating-system environment variable
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY was not found. "
            "For Streamlit Cloud, add it under App Settings > Secrets. "
            "For local development, add it to the .env file."
        )

    return api_key


def create_llm():
    """
    Create and return the Groq chat model.
    """

    api_key = get_groq_api_key()

    llm = ChatGroq(
        groq_api_key=api_key,
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_retries=2
    )

    return llm


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