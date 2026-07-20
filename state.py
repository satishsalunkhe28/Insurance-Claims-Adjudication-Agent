from typing import List, TypedDict

from langchain_core.documents import Document


class ClaimState(TypedDict, total=False):

    # Customer claim details
    policy_number: str
    customer_name: str
    incident_type: str
    incident_description: str
    claim_amount: float

    # Retrieval details
    search_query: str
    retrieved_documents: List[Document]

    # Coverage analysis
    coverage_status: str
    coverage_reason: str

    # Final decision
    final_decision: str
    final_reason: str
    confidence: float


if __name__ == "__main__":

    test_state: ClaimState = {
        "policy_number": "POL-1001",
        "customer_name": "Satish Salunkhe",
        "incident_type": "Flood Damage",
        "incident_description": (
            "Water entered the engine while driving through a flooded road."
        ),
        "claim_amount": 75000.0
    }

    print("Claim State Created Successfully")

    print("\nPolicy Number:")
    print(test_state["policy_number"])

    print("\nCustomer Name:")
    print(test_state["customer_name"])

    print("\nIncident Type:")
    print(test_state["incident_type"])

    print("\nIncident Description:")
    print(test_state["incident_description"])

    print("\nClaim Amount:")
    print(test_state["claim_amount"])