"""LangGraph nodes for retrieval and insurance claim adjudication."""

from typing import Literal

from pydantic import BaseModel, Field

from llm import create_llm
from prompts import COVERAGE_ANALYSIS_PROMPT
from retriever import search_policy
from state import ClaimState


class CoverageResult(BaseModel):
    """Detailed structured result returned by the LLM."""

    coverage_status: Literal[
        "covered",
        "not_covered",
        "unclear",
    ]

    decision_summary: str = Field(
        min_length=10,
        description="One clear sentence describing the coverage result.",
    )

    detailed_explanation: str = Field(
        min_length=80,
        description=(
            "A detailed explanation in simple professional English, "
            "grounded only in the retrieved documents."
        ),
    )

    policy_basis: str = Field(
        min_length=10,
        description=(
            "The relevant policy clause or rule and source filename."
        ),
    )

    recommendation: str = Field(
        min_length=10,
        description="One practical next step for the claim.",
    )


FINAL_DECISION_MAP = {
    "covered": {
        "final_decision": "approved",
        "confidence": 0.94,
    },
    "not_covered": {
        "final_decision": "claim_not_covered",
        "confidence": 0.92,
    },
    "unclear": {
        "final_decision": "manual_review_required",
        "confidence": 0.58,
    },
}


def retrieve_policy_documents(state: ClaimState) -> dict:
    """Retrieve relevant coverage, exclusion and endorsement sections."""

    incident_type = str(state.get("incident_type", "")).strip()
    incident_description = str(
        state.get("incident_description", "")
    ).strip()

    if not incident_description:
        return {
            "search_query": "",
            "retrieved_documents": [],
        }

    search_query = (
        "Private motor insurance claim assessment. "
        f"Incident type: {incident_type}. "
        f"Incident facts: {incident_description}. "
        "Retrieve relevant basic coverage, exclusions, endorsements, "
        "conditions, required documents, settlement and manual-review rules."
    )

    retrieved_documents = search_policy(search_query)

    return {
        "search_query": search_query,
        "retrieved_documents": retrieved_documents,
    }


def create_policy_context(retrieved_documents) -> str:
    """Create a grounded context block from retrieved documents."""

    sections = []

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

        sections.append(
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

    return "\n\n---\n\n".join(sections)


def analyze_coverage(state: ClaimState) -> dict:
    """Analyze coverage and create a detailed grounded explanation."""

    retrieved_documents = state.get(
        "retrieved_documents",
        [],
    )

    if not retrieved_documents:
        return {
            "coverage_status": "unclear",
            "decision_summary": (
                "Coverage could not be determined automatically."
            ),
            "coverage_reason": (
                "No relevant policy documents were retrieved. "
                "The claim must be reviewed after the policy documents "
                "and applicable clauses are made available."
            ),
            "policy_basis": (
                "No policy source was available for this assessment."
            ),
            "recommendation": (
                "Verify the policy-document index and refer the claim "
                "to a human adjuster."
            ),
        }

    prompt = COVERAGE_ANALYSIS_PROMPT.format(
        policy_number=state.get(
            "policy_number",
            "Not provided",
        ),
        incident_type=state.get(
            "incident_type",
            "Not provided",
        ),
        incident_description=state.get(
            "incident_description",
            "Not provided",
        ),
        claim_amount=state.get(
            "claim_amount",
            0,
        ),
        policy_context=create_policy_context(
            retrieved_documents
        ),
    )

    try:
        structured_llm = create_llm().with_structured_output(
            CoverageResult
        )
        result = structured_llm.invoke(prompt)

        if result is None:
            raise ValueError(
                "The LLM returned no structured result."
            )

        return {
            "coverage_status": result.coverage_status,
            "decision_summary": result.decision_summary.strip(),
            "coverage_reason": result.detailed_explanation.strip(),
            "policy_basis": result.policy_basis.strip(),
            "recommendation": result.recommendation.strip(),
        }

    except Exception as error:
        print(
            "Coverage analysis failed: "
            f"{type(error).__name__}: {error}"
        )

        return {
            "coverage_status": "unclear",
            "decision_summary": (
                "The automated analysis could not be completed."
            ),
            "coverage_reason": (
                "A technical issue prevented the AI from completing "
                "the policy analysis. This is not a coverage denial. "
                "The claim should be reviewed after the application "
                "configuration or model connection is corrected."
            ),
            "policy_basis": (
                "No reliable policy conclusion was produced because "
                "the automated analysis failed."
            ),
            "recommendation": (
                "Check the Groq API configuration and application logs, "
                "then run the claim again."
            ),
        }


def make_final_decision(state: ClaimState) -> dict:
    """Convert coverage status into a deterministic final decision."""

    coverage_status = str(
        state.get(
            "coverage_status",
            "unclear",
        )
    ).strip().lower()

    decision = FINAL_DECISION_MAP.get(
        coverage_status,
        FINAL_DECISION_MAP["unclear"],
    )

    summary = str(
        state.get(
            "decision_summary",
            "Coverage assessment completed.",
        )
    ).strip()

    explanation = str(
        state.get(
            "coverage_reason",
            "Coverage information is unavailable.",
        )
    ).strip()

    policy_basis = str(
        state.get(
            "policy_basis",
            "Policy basis is unavailable.",
        )
    ).strip()

    recommendation = str(
        state.get(
            "recommendation",
            "Refer the claim for review.",
        )
    ).strip()

    final_reason = (
        f"{summary}\n\n"
        f"{explanation}\n\n"
        f"Policy basis: {policy_basis}\n\n"
        f"Recommended next step: {recommendation}"
    )

    return {
        "final_decision": decision["final_decision"],
        "final_reason": final_reason,
        "confidence": decision["confidence"],
    }


def create_fallback_decision(
    coverage_status: str,
    coverage_reason: str,
) -> dict:
    """Backward-compatible fallback helper."""

    return make_final_decision(
        {
            "coverage_status": coverage_status,
            "coverage_reason": coverage_reason,
        }
    )