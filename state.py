from typing import List, TypedDict

from langchain_core.documents import Document


class ClaimState(TypedDict, total=False):
    # Claim details
    policy_number: str
    customer_name: str
    incident_type: str
    incident_description: str
    claim_amount: float

    # Retrieval
    search_query: str
    retrieved_documents: List[Document]

    # Coverage analysis
    coverage_status: str
    decision_summary: str
    coverage_reason: str
    policy_basis: str
    recommendation: str

    # Final decision
    final_decision: str
    final_reason: str
    confidence: float