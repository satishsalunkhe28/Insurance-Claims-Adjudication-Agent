import streamlit as st

from graph import claim_graph
from state import ClaimState


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="ClaimGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def format_status(value: str) -> str:
    """
    Convert values such as manual_review_required
    into Manual Review Required.
    """

    if not value:
        return "Not Available"

    return value.replace("_", " ").title()


def show_decision_status(final_decision: str):
    """
    Display the final claim status.
    """

    if final_decision == "approved":
        st.success("✅ Claim Approved")

    elif final_decision == "claim_not_covered":
        st.error("❌ Claim Not Covered")

    else:
        st.warning("⚠️ Manual Review Required")


def show_policy_sources(retrieved_documents):
    """
    Display the policy documents retrieved by the RAG system.
    """

    if not retrieved_documents:
        st.info("No relevant policy documents were retrieved.")
        return

    st.caption(
        f"{len(retrieved_documents)} policy sections "
        "were used for this claim analysis."
    )

    for index, document in enumerate(
        retrieved_documents,
        start=1
    ):
        file_name = document.metadata.get(
            "file_name",
            "Unknown Source"
        )

        source = document.metadata.get(
            "source",
            "Source path not available"
        )

        with st.expander(
            f"Source {index}: {file_name}"
        ):
            st.caption(f"Source: {source}")
            st.write(document.page_content)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.title("🛡️ ClaimGuard AI")

    st.caption(
        "Insurance Claims Adjudication Agent"
    )

    st.divider()

    st.subheader("Navigation")

    st.button(
        "📄 New Claim",
        use_container_width=True
    )

    st.button(
        "📑 Claim History",
        use_container_width=True,
        disabled=True
    )

    st.button(
        "📚 Policy Documents",
        use_container_width=True,
        disabled=True
    )

    st.button(
        "📊 Dashboard",
        use_container_width=True,
        disabled=True
    )

    st.divider()

    st.caption("Version 1.0")


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

header_column, status_column = st.columns(
    [5, 1]
)

with header_column:

    st.title("Insurance Claims Adjudication")

    st.write(
        """
        Submit a motor insurance claim and receive an
        AI-assisted coverage analysis based on the available
        policy documents.
        """
    )

with status_column:

    st.metric(
        label="Application",
        value="Online"
    )


st.divider()


# ---------------------------------------------------------
# NEW CLAIM FORM
# ---------------------------------------------------------

st.subheader("New Claim")

st.caption(
    "Enter the customer, policy and incident details below."
)


with st.form("claim_form"):

    customer_column, policy_column = st.columns(2)

    with customer_column:

        customer_name = st.text_input(
            "Customer Name *",
            placeholder="Example: Rahul Sharma"
        )

    with policy_column:

        policy_number = st.text_input(
            "Policy Number *",
            placeholder="Example: POL-1001"
        )

    incident_column, amount_column = st.columns(
        [2, 1]
    )

    with incident_column:

        incident_type = st.selectbox(
            "Incident Type *",
            options=[
                "Accident Damage",
                "Flood Damage",
                "Theft",
                "Fire Damage",
                "Engine Damage",
                "Natural Disaster",
                "Third-Party Damage",
                "Other"
            ]
        )

    with amount_column:

        claim_amount = st.number_input(
            "Claim Amount ₹ *",
            min_value=0.0,
            step=1000.0,
            format="%.2f"
        )

    incident_description = st.text_area(
        "Incident Description *",
        placeholder=(
            "Describe what happened, where it happened "
            "and how the vehicle was damaged."
        ),
        height=160
    )

    confirm_details = st.checkbox(
        "I confirm that the entered claim details are correct."
    )

    submitted = st.form_submit_button(
        "Analyze Claim",
        type="primary",
        use_container_width=True
    )


# ---------------------------------------------------------
# CLAIM PROCESSING
# ---------------------------------------------------------

if submitted:

    validation_errors = []

    if not customer_name.strip():
        validation_errors.append(
            "Customer name is required."
        )

    if not policy_number.strip():
        validation_errors.append(
            "Policy number is required."
        )

    if not incident_description.strip():
        validation_errors.append(
            "Incident description is required."
        )

    if claim_amount <= 0:
        validation_errors.append(
            "Claim amount must be greater than zero."
        )

    if not confirm_details:
        validation_errors.append(
            "Please confirm that the claim details are correct."
        )

    if validation_errors:

        st.error(
            "Please correct the following details:"
        )

        for validation_error in validation_errors:
            st.write(f"- {validation_error}")

    else:

        initial_state: ClaimState = {
            "policy_number": policy_number.strip(),
            "customer_name": customer_name.strip(),
            "incident_type": incident_type,
            "incident_description": (
                incident_description.strip()
            ),
            "claim_amount": float(claim_amount)
        }

        try:

            with st.status(
                "Processing insurance claim...",
                expanded=True
            ) as status:

                st.write(
                    "1. Claim information received."
                )

                st.write(
                    "2. Retrieving relevant policy documents."
                )

                final_state = claim_graph.invoke(
                    initial_state
                )

                st.write(
                    "3. Coverage analysis completed."
                )

                st.write(
                    "4. Final decision generated."
                )

                status.update(
                    label="Claim processing completed",
                    state="complete",
                    expanded=False
                )

            st.divider()

            # -------------------------------------------------
            # CLAIM RESULT
            # -------------------------------------------------

            st.subheader("Claim Result")

            final_decision = final_state.get(
                "final_decision",
                "manual_review_required"
            )

            coverage_status = final_state.get(
                "coverage_status",
                "unclear"
            )

            confidence = float(
                final_state.get(
                    "confidence",
                    0
                )
            )

            show_decision_status(
                final_decision
            )

            # -------------------------------------------------
            # CLAIM SUMMARY
            # -------------------------------------------------

            st.subheader("Claim Summary")

            summary_column1, summary_column2 = st.columns(2)

            with summary_column1:

                st.text_input(
                    "Customer Name",
                    value=final_state.get(
                        "customer_name",
                        "Not Available"
                    ),
                    disabled=True
                )

                st.text_input(
                    "Incident Type",
                    value=final_state.get(
                        "incident_type",
                        "Not Available"
                    ),
                    disabled=True
                )

            with summary_column2:

                st.text_input(
                    "Policy Number",
                    value=final_state.get(
                        "policy_number",
                        "Not Available"
                    ),
                    disabled=True
                )

                st.text_input(
                    "Claim Amount",
                    value=(
                        f"₹{final_state.get('claim_amount', 0):,.2f}"
                    ),
                    disabled=True
                )

            metric_column1, metric_column2, metric_column3 = (
                st.columns(3)
            )

            with metric_column1:

                st.metric(
                    "Final Decision",
                    format_status(
                        final_decision
                    )
                )

            with metric_column2:

                st.metric(
                    "Coverage Status",
                    format_status(
                        coverage_status
                    )
                )

            with metric_column3:

                st.metric(
                    "Confidence",
                    f"{confidence * 100:.0f}%"
                )

            st.progress(
                min(
                    max(confidence, 0.0),
                    1.0
                )
            )

            # -------------------------------------------------
            # RESULT DETAILS
            # -------------------------------------------------

            analysis_tab, decision_tab, sources_tab = st.tabs(
                [
                    "Coverage Analysis",
                    "Final Decision",
                    "Policy Sources"
                ]
            )

            with analysis_tab:

                st.subheader("Coverage Analysis")

                st.write(
                    final_state.get(
                        "coverage_reason",
                        "Coverage reason is not available."
                    )
                )

            with decision_tab:

                st.subheader("Final Decision")

                st.write(
                    f"**Decision:** "
                    f"{format_status(final_decision)}"
                )

                st.write(
                    f"**Reason:** "
                    f"{final_state.get(
                        'final_reason',
                        'Final reason is not available.'
                    )}"
                )

                st.write(
                    f"**Confidence:** "
                    f"{confidence * 100:.0f}%"
                )

            with sources_tab:

                st.subheader(
                    "Retrieved Policy Documents"
                )

                retrieved_documents = final_state.get(
                    "retrieved_documents",
                    []
                )

                show_policy_sources(
                    retrieved_documents
                )

        except Exception as error:

            st.error(
                "The claim analysis could not be completed."
            )

            st.warning(
                "Check the API key, vector database and terminal logs."
            )

            with st.expander(
                "View Technical Error"
            ):
                st.exception(error)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "ClaimGuard AI is a demonstration application. "
    "Final insurance decisions should be verified by "
    "an authorized insurance adjuster."
)