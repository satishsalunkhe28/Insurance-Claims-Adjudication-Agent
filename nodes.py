from typing import Literal

from pydantic import BaseModel, Field

from llm import create_llm
from prompts import (
    COVERAGE_ANALYSIS_PROMPT,
    FINAL_DECISION_PROMPT
)
from retriever import search_policy
from state import ClaimState


class CoverageResult(BaseModel):
    """
    Structured coverage result returned by the LLM.
    """

    coverage_status: Literal[
        "covered",
        "not_covered",
        "unclear"
    ] = Field(
        description=(
            "Coverage result based only on the retrieved "
            "insurance policy documents."
        )
    )

    coverage_reason: str = Field(
        description=(
            "A clear and short explanation supported by "
            "the retrieved policy documents."
        )
    )


class FinalDecisionResult(BaseModel):
    """
    Structured final claim decision returned by the LLM.
    """

    final_decision: Literal[
        "approved",
        "claim_not_covered",
        "manual_review_required"
    ] = Field(
        description=(
            "The final decision for the insurance claim."
        )
    )

    final_reason: str = Field(
        description=(
            "A short and professional explanation "
            "for the final decision."
        )
    )

    confidence: float = Field(
        ge=0,
        le=1,
        description=(
            "Confidence score between 0 and 1."
        )
    )


def retrieve_policy_documents(
    state: ClaimState
) -> dict:
    """
    Search the vector database using the incident details.

    Returns:
    - search_query
    - retrieved_documents
    """

    print("\nRetrieval Node Started")

    incident_type = state.get(
        "incident_type",
        ""
    )

    incident_description = state.get(
        "incident_description",
        ""
    )

    if not incident_description:
        print("Incident description is missing.")

        return {
            "search_query": "",
            "retrieved_documents": []
        }

    search_query = (
        f"Incident type: {incident_type}. "
        f"Incident description: {incident_description}"
    )

    retrieved_documents = search_policy(
        search_query
    )

    print(
        f"Documents Retrieved: "
        f"{len(retrieved_documents)}"
    )

    return {
        "search_query": search_query,
        "retrieved_documents": retrieved_documents
    }


def create_policy_context(
    retrieved_documents
) -> str:
    """
    Combine retrieved policy chunks into one text block.

    It also includes the source filename for every chunk.
    """

    policy_context_parts = []

    for index, document in enumerate(
        retrieved_documents,
        start=1
    ):
        file_name = document.metadata.get(
            "file_name",
            "Unknown source"
        )

        source = document.metadata.get(
            "source",
            "Unknown path"
        )

        document_text = (
            f"Document {index}\n"
            f"File Name: {file_name}\n"
            f"Source: {source}\n"
            f"Content:\n{document.page_content}"
        )

        policy_context_parts.append(
            document_text
        )

    return "\n\n".join(
        policy_context_parts
    )


def analyze_coverage(
    state: ClaimState
) -> dict:
    """
    Analyze whether the claim is covered.

    Returns:
    - coverage_status
    - coverage_reason
    """

    print("\nCoverage Analysis Node Started")

    retrieved_documents = state.get(
        "retrieved_documents",
        []
    )

    if not retrieved_documents:
        print(
            "No policy documents are available "
            "for coverage analysis."
        )

        return {
            "coverage_status": "unclear",
            "coverage_reason": (
                "No relevant policy documents were retrieved. "
                "The claim requires manual review."
            )
        }

    policy_context = create_policy_context(
        retrieved_documents
    )

    prompt = COVERAGE_ANALYSIS_PROMPT.format(
        policy_number=state.get(
            "policy_number",
            "Not provided"
        ),
        incident_type=state.get(
            "incident_type",
            "Not provided"
        ),
        incident_description=state.get(
            "incident_description",
            "Not provided"
        ),
        claim_amount=state.get(
            "claim_amount",
            0
        ),
        policy_context=policy_context
    )

    try:
        llm = create_llm()

        structured_llm = (
            llm.with_structured_output(
                CoverageResult
            )
        )

        result = structured_llm.invoke(
            prompt
        )

        print("\nCoverage Status:")
        print(result.coverage_status)

        print("\nCoverage Reason:")
        print(result.coverage_reason)

        return {
            "coverage_status": (
                result.coverage_status
            ),
            "coverage_reason": (
                result.coverage_reason
            )
        }

    except Exception as error:
        print(
            "\nCoverage analysis failed:"
        )
        print(error)

        return {
            "coverage_status": "unclear",
            "coverage_reason": (
                "The AI coverage analysis could not be "
                "completed. Manual review is required."
            )
        }


def make_final_decision(
    state: ClaimState
) -> dict:
    """
    Convert coverage analysis into a final claim decision.

    Returns:
    - final_decision
    - final_reason
    - confidence
    """

    print("\nFinal Decision Node Started")

    coverage_status = state.get(
        "coverage_status",
        "unclear"
    )

    coverage_reason = state.get(
        "coverage_reason",
        "Coverage information is unavailable."
    )

    prompt = FINAL_DECISION_PROMPT.format(
        coverage_status=coverage_status,
        coverage_reason=coverage_reason
    )

    try:
        llm = create_llm()

        structured_llm = (
            llm.with_structured_output(
                FinalDecisionResult
            )
        )

        result = structured_llm.invoke(
            prompt
        )

        print("\nFinal Decision:")
        print(result.final_decision)

        print("\nFinal Reason:")
        print(result.final_reason)

        print("\nConfidence:")
        print(result.confidence)

        return {
            "final_decision": (
                result.final_decision
            ),
            "final_reason": (
                result.final_reason
            ),
            "confidence": (
                result.confidence
            )
        }

    except Exception as error:
        print(
            "\nFinal decision generation failed:"
        )
        print(error)

        return create_fallback_decision(
            coverage_status=coverage_status,
            coverage_reason=coverage_reason
        )


def create_fallback_decision(
    coverage_status: str,
    coverage_reason: str
) -> dict:
    """
    Create a rule-based decision if the LLM fails.
    """

    if coverage_status == "covered":
        return {
            "final_decision": "approved",
            "final_reason": coverage_reason,
            "confidence": 0.80
        }

    if coverage_status == "not_covered":
        return {
            "final_decision": (
                "claim_not_covered"
            ),
            "final_reason": coverage_reason,
            "confidence": 0.80
        }

    return {
        "final_decision": (
            "manual_review_required"
        ),
        "final_reason": (
            coverage_reason
            or
            "The available policy information is unclear."
        ),
        "confidence": 0.50
    }


if __name__ == "__main__":

    test_state: ClaimState = {
        "policy_number": "POL-1001",
        "customer_name": "Satish Salunkhe",
        "incident_type": "Flood Damage",
        "incident_description": (
            "Water entered the vehicle engine "
            "while driving through a flooded road."
        ),
        "claim_amount": 75000.0
    }

    print("\n" + "=" * 70)
    print("Initial Claim State")
    print("=" * 70)

    print(test_state)

    retrieval_result = (
        retrieve_policy_documents(
            test_state
        )
    )

    test_state.update(
        retrieval_result
    )

    print("\n" + "=" * 70)
    print("Retrieved Documents")
    print("=" * 70)

    retrieved_documents = test_state.get(
        "retrieved_documents",
        []
    )

    if not retrieved_documents:
        print(
            "No documents were retrieved."
        )

    for index, document in enumerate(
        retrieved_documents,
        start=1
    ):
        print("\n" + "-" * 70)
        print(f"Document {index}")

        print(
            "File:",
            document.metadata.get(
                "file_name",
                "Unknown"
            )
        )

        print("\nContent:")
        print(document.page_content)

    coverage_result = analyze_coverage(
        test_state
    )

    test_state.update(
        coverage_result
    )

    print("\n" + "=" * 70)
    print("Coverage Analysis Result")
    print("=" * 70)

    print(
        "\nCoverage Status:",
        test_state.get(
            "coverage_status"
        )
    )

    print(
        "\nCoverage Reason:",
        test_state.get(
            "coverage_reason"
        )
    )

    decision_result = make_final_decision(
        test_state
    )

    test_state.update(
        decision_result
    )

    print("\n" + "=" * 70)
    print("Final Claim Decision")
    print("=" * 70)

    print(
        "\nDecision:",
        test_state.get(
            "final_decision"
        )
    )

    print(
        "\nReason:",
        test_state.get(
            "final_reason"
        )
    )

    print(
        "\nConfidence:",
        test_state.get(
            "confidence"
        )
    )

    print("\n" + "=" * 70)
    print("Complete Final State")
    print("=" * 70)

    print(test_state)