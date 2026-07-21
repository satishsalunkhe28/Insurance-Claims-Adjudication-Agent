"""LangGraph nodes for insurance claim retrieval and adjudication."""

from typing import Literal

from pydantic import BaseModel, Field

from llm import create_llm
from prompts import COVERAGE_ANALYSIS_PROMPT
from retriever import search_policy
from state import ClaimState


class CoverageResult(BaseModel):
    """Structured coverage result returned by the LLM."""

    coverage_status: Literal[
        "covered",
        "not_covered",
        "unclear",
    ] = Field(
        description=(
            "Use covered for a clearly covered event, not_covered for a "
            "clear exclusion, and unclear only when coverage cannot be "
            "reliably determined from the supplied documents."
        )
    )

    coverage_reason: str = Field(
        min_length=5,
        description=(
            "A concise reason grounded in the retrieved policy documents, "
            "including the relevant source filename when possible."
        ),
    )


FINAL_DECISION_MAP = {
    "covered": {
        "final_decision": "approved",
        "confidence": 0.92,
    },
    "not_covered": {
        "final_decision": "claim_not_covered",
        "confidence": 0.92,
    },
    "unclear": {
        "final_decision": "manual_review_required",
        "confidence": 0.55,
    },
}


def retrieve_policy_documents(state: ClaimState) -> dict:
    """Retrieve relevant policy chunks using the incident details."""

    print("\nRetrieval Node Started")

    incident_type = str(state.get("incident_type", "")).strip()
    incident_description = str(
        state.get("incident_description", "")
    ).strip()

    if not incident_description:
        print("Incident description is missing.")
        return {
            "search_query": "",
            "retrieved_documents": [],
        }

    # Add insurance-specific concepts to improve retrieval of coverage,
    # exclusions, endorsements, conditions, and manual-review clauses.
    search_query = (
        f"Private motor insurance claim. "
        f"Incident type: {incident_type}. "
        f"Incident description: {incident_description}. "
        "Find applicable basic coverage, exclusions, endorsements, "
        "policy conditions, and manual review rules."
    )

    try:
        retrieved_documents = search_policy(search_query)
    except Exception as error:
        print(f"Policy retrieval failed: {error}")
        retrieved_documents = []

    print(f"Documents Retrieved: {len(retrieved_documents)}")

    return {
        "search_query": search_query,
        "retrieved_documents": retrieved_documents,
    }


def create_policy_context(retrieved_documents) -> str:
    """Combine retrieved policy chunks into one grounded context block."""

    policy_context_parts = []

    for index, document in enumerate(retrieved_documents, start=1):
        file_name = document.metadata.get(
            "file_name",
            "Unknown source",
        )
        source = document.metadata.get(
            "source",
            "Unknown path",
        )
        category = document.metadata.get(
            "category",
            "Unknown category",
        )

        policy_context_parts.append(
            "\n".join(
                [
                    f"Document {index}",
                    f"File Name: {file_name}",
                    f"Category: {category}",
                    f"Source: {source}",
                    "Content:",
                    document.page_content,
                ]
            )
        )

    return "\n\n---\n\n".join(policy_context_parts)


def analyze_coverage(state: ClaimState) -> dict:
    """Analyze claim coverage using retrieved policy documents."""

    print("\nCoverage Analysis Node Started")

    retrieved_documents = state.get("retrieved_documents", [])

    if not retrieved_documents:
        return {
            "coverage_status": "unclear",
            "coverage_reason": (
                "No relevant policy documents were retrieved, so coverage "
                "cannot be determined automatically."
            ),
        }

    policy_context = create_policy_context(retrieved_documents)

    prompt = COVERAGE_ANALYSIS_PROMPT.format(
        policy_number=state.get("policy_number", "Not provided"),
        incident_type=state.get("incident_type", "Not provided"),
        incident_description=state.get(
            "incident_description",
            "Not provided",
        ),
        claim_amount=state.get("claim_amount", 0),
        policy_context=policy_context,
    )

    try:
        llm = create_llm()
        structured_llm = llm.with_structured_output(CoverageResult)
        result = structured_llm.invoke(prompt)

        if result is None:
            raise ValueError("The LLM returned no structured coverage result.")

        coverage_status = str(result.coverage_status).strip().lower()
        coverage_reason = str(result.coverage_reason).strip()

        if coverage_status not in FINAL_DECISION_MAP:
            raise ValueError(
                f"Unexpected coverage status: {coverage_status}"
            )

        print(f"Coverage Status: {coverage_status}")
        print(f"Coverage Reason: {coverage_reason}")

        return {
            "coverage_status": coverage_status,
            "coverage_reason": coverage_reason,
        }

    except Exception as error:
        # Keep the real error in Streamlit logs so configuration/model issues
        # are visible instead of silently appearing as a normal manual review.
        print(f"Coverage analysis failed: {type(error).__name__}: {error}")

        return {
            "coverage_status": "unclear",
            "coverage_reason": (
                "The automated coverage analysis could not be completed. "
                f"Technical details: {type(error).__name__}: {error}"
            ),
        }


def make_final_decision(state: ClaimState) -> dict:
    """Map coverage status to a deterministic final decision."""

    print("\nFinal Decision Node Started")

    coverage_status = str(
        state.get("coverage_status", "unclear")
    ).strip().lower()
    coverage_reason = str(
        state.get(
            "coverage_reason",
            "Coverage information is unavailable.",
        )
    ).strip()

    decision = FINAL_DECISION_MAP.get(
        coverage_status,
        FINAL_DECISION_MAP["unclear"],
    )

    final_result = {
        "final_decision": decision["final_decision"],
        "final_reason": coverage_reason,
        "confidence": decision["confidence"],
    }

    print(f"Final Decision: {final_result['final_decision']}")
    print(f"Final Reason: {final_result['final_reason']}")
    print(f"Confidence: {final_result['confidence']}")

    return final_result


def create_fallback_decision(
    coverage_status: str,
    coverage_reason: str,
) -> dict:
    """Backward-compatible wrapper around the deterministic decision map."""

    return make_final_decision(
        {
            "coverage_status": coverage_status,
            "coverage_reason": coverage_reason,
        }
    )


if __name__ == "__main__":
    test_state: ClaimState = {
        "policy_number": "POL-1001",
        "customer_name": "Satish Salunkhe",
        "incident_type": "Road Accident",
        "incident_description": (
            "The insured car collided with another vehicle and the front "
            "bumper and headlight were damaged."
        ),
        "claim_amount": 75000.0,
    }

    retrieval_result = retrieve_policy_documents(test_state)
    test_state.update(retrieval_result)

    coverage_result = analyze_coverage(test_state)
    test_state.update(coverage_result)

    decision_result = make_final_decision(test_state)
    test_state.update(decision_result)

    print("\nComplete Final State")
    print(test_state)