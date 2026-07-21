import streamlit as st

from graph import claim_graph
from llm import create_llm
from state import ClaimState


# ---------------------------------------------------------
# PAGE SETTINGS
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

def format_text(value: str) -> str:
    """
    Convert values like manual_review_required
    into Manual Review Required.
    """

    if not value:
        return "Not Available"

    return value.replace("_", " ").title()


@st.cache_resource
def check_application_status():
    """
    Check whether the Groq LLM can be created.
    """

    try:
        create_llm()
        return True, "Application is connected to the Groq LLM."

    except Exception as error:
        return False, str(error)


def show_application_status():
    """
    Show application status:
    Online  -> Green
    Offline -> Red
    """

    is_online, status_message = check_application_status()

    if is_online:
        st.success("🟢 Application Online")
    else:
        st.error("🔴 Application Offline")

        with st.expander("View Error Details"):
            st.write(status_message)


def show_final_decision(final_decision: str):
    """
    Show the final decision using colors.

    Approved               -> Green
    Claim Not Covered      -> Red
    Manual Review Required -> Yellow
    """

    decision = (
        final_decision or ""
    ).strip().lower()

    if decision == "approved":
        st.success("✅ Claim Approved")

    elif decision == "claim_not_covered":
        st.error("❌ Claim Not Covered")

    elif decision == "manual_review_required":
        st.warning("⚠️ Manual Review Required")

    else:
        st.info(
            f"ℹ️ {format_text(decision)}"
        )


def show_policy_sources(retrieved_documents):
    """
    Display the policy documents used by the agent.
    """

    if not retrieved_documents:
        st.info(
            "No relevant policy documents were retrieved."
        )
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
    [4, 1]
)

with header_column:

    st.title("Insurance Claims Adjudication")

    st.write(
        """
        Submit a private motor insurance claim and receive
        an AI-assisted coverage analysis based on the
        available policy documents.
        """
    )

with status_column:
    show_application_status()


st.divider()


# ---------------------------------------------------------
# CLAIM FORM
# ---------------------------------------------------------

st.subheader("New Claim")

st.caption(
    "Enter the customer, policy and incident details."
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
                "Road Accident",
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
            "Explain what happened, where it happened, "
            "the damage caused and the documents submitted."
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

    errors = []

    if not customer_name.strip():
        errors.append("Customer name is required.")

    if not policy_number.strip():
        errors.append("Policy number is required.")

    if not incident_description.strip():
        errors.append("Incident description is required.")

    if claim_amount <= 0:
        errors.append(
            "Claim amount must be greater than zero."
        )

    if not confirm_details:
        errors.append(
            "Please confirm that the claim details are correct."
        )

    if errors:

        st.error(
            "Please correct the following details:"
        )

        for error in errors:
            st.write(f"- {error}")

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
            ) as processing_status:

                st.write(
                    "1. Claim details received."
                )

                st.write(
                    "2. Searching relevant policy documents."
                )

                final_state = claim_graph.invoke(
                    initial_state
                )

                st.write(
                    "3. Coverage analysis completed."
                )

                st.write(
                    "4. Final decision created."
                )

                processing_status.update(
                    label="Claim processing completed",
                    state="complete",
                    expanded=False
                )

            st.divider()

            # -------------------------------------------------
            # RESULT VALUES
            # -------------------------------------------------

            final_decision = final_state.get(
                "final_decision",
                "manual_review_required"
            )

            coverage_status = final_state.get(
                "coverage_status",
                "unclear"
            )

            coverage_reason = final_state.get(
                "coverage_reason",
                "Coverage reason is not available."
            )

            final_reason = final_state.get(
                "final_reason",
                "Final explanation is not available."
            )

            confidence = float(
                final_state.get(
                    "confidence",
                    0
                )
            )

            # -------------------------------------------------
            # MAIN RESULT
            # -------------------------------------------------

            st.subheader("Claim Result")

            show_final_decision(
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
                    format_text(
                        final_decision
                    )
                )

            with metric_column2:

                st.metric(
                    "Coverage Status",
                    format_text(
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
            # DETAIL TABS
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

                if coverage_status == "covered":
                    st.success(
                        f"Coverage Status: "
                        f"{format_text(coverage_status)}"
                    )

                elif coverage_status == "not_covered":
                    st.error(
                        f"Coverage Status: "
                        f"{format_text(coverage_status)}"
                    )

                else:
                    st.warning(
                        f"Coverage Status: "
                        f"{format_text(coverage_status)}"
                    )

                st.markdown("### Analysis")

                st.info(coverage_reason)

            with decision_tab:

                st.subheader("Final Decision")

                show_final_decision(
                    final_decision
                )

                st.markdown("### Explanation")

                st.info(final_reason)

                st.markdown("### Confidence")

                st.write(
                    f"{confidence * 100:.0f}%"
                )

                st.progress(
                    min(
                        max(confidence, 0.0),
                        1.0
                    )
                )

                st.caption(
                    "The final decision is based on the "
                    "retrieved policy documents and the "
                    "submitted claim details."
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
                "Check the Groq API key, vector database "
                "and Streamlit application logs."
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