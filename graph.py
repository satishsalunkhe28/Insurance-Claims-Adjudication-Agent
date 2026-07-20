from langgraph.graph import END, START, StateGraph

from nodes import (
    analyze_coverage,
    make_final_decision,
    retrieve_policy_documents
)
from state import ClaimState


def create_claim_graph():
    """
    Create and compile the insurance claim workflow.

    Workflow:

    START
      ↓
    retrieve_policy_documents
      ↓
    analyze_coverage
      ↓
    make_final_decision
      ↓
    END
    """

    graph_builder = StateGraph(ClaimState)

    graph_builder.add_node(
        "retrieve_policy_documents",
        retrieve_policy_documents
    )

    graph_builder.add_node(
        "analyze_coverage",
        analyze_coverage
    )

    graph_builder.add_node(
        "make_final_decision",
        make_final_decision
    )

    graph_builder.add_edge(
        START,
        "retrieve_policy_documents"
    )

    graph_builder.add_edge(
        "retrieve_policy_documents",
        "analyze_coverage"
    )

    graph_builder.add_edge(
        "analyze_coverage",
        "make_final_decision"
    )

    graph_builder.add_edge(
        "make_final_decision",
        END
    )

    compiled_graph = graph_builder.compile()

    return compiled_graph


claim_graph = create_claim_graph()


if __name__ == "__main__":

    initial_state: ClaimState = {
        "policy_number": "POL-1001",
        "customer_name": "Satish Salunkhe",
        "incident_type": "Flood Damage",
        "incident_description": (
            "Water entered the vehicle engine while "
            "driving through a flooded road."
        ),
        "claim_amount": 75000.0
    }

    print("\n" + "=" * 70)
    print("Insurance Claim Workflow Started")
    print("=" * 70)

    final_state = claim_graph.invoke(
        initial_state
    )

    print("\n" + "=" * 70)
    print("Insurance Claim Workflow Completed")
    print("=" * 70)

    print("\nPolicy Number:")
    print(final_state.get("policy_number"))

    print("\nCustomer Name:")
    print(final_state.get("customer_name"))

    print("\nCoverage Status:")
    print(final_state.get("coverage_status"))

    print("\nCoverage Reason:")
    print(final_state.get("coverage_reason"))

    print("\nFinal Decision:")
    print(final_state.get("final_decision"))

    print("\nFinal Reason:")
    print(final_state.get("final_reason"))

    print("\nConfidence:")
    print(final_state.get("confidence"))

    print("\nRetrieved Sources:")

    retrieved_documents = final_state.get(
        "retrieved_documents",
        []
    )

    for index, document in enumerate(
        retrieved_documents,
        start=1
    ):
        file_name = document.metadata.get(
            "file_name",
            "Unknown source"
        )

        print(f"{index}. {file_name}")