import streamlit as st

from graph import claim_graph
from state import ClaimState


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="ClaimGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def format_status(value: str) -> str:
    """
    Convert values such as:
    manual_review_required

    Into:
    Manual Review Required
    """

    if not value:
        return "Not Available"

    return str(value).replace("_", " ").title()


def normalize_confidence(value) -> float:
    """
    Convert confidence into a value between 0 and 1.
    """

    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.0

    if confidence > 1:
        confidence = confidence / 100

    return min(max(confidence, 0.0), 1.0)


def show_decision_status(final_decision: str) -> None:
    """
    Display claim decision using native Streamlit messages.
    """

    if final_decision == "approved":
        st.success("✅ Claim Approved")

    elif final_decision == "claim_not_covered":
        st.error("❌ Claim Not Covered")

    elif final_decision == "denied":
        st.error("❌ Claim Denied")

    else:
        st.warning("⚠️ Manual Review Required")


def show_policy_sources(retrieved_documents) -> None:
    """
    Display policy documents retrieved by the RAG system.
    """

    if not retrieved_documents:
        st.info("No relevant policy documents were retrieved.")
        return

    st.caption(
        f"{len(retrieved_documents)} policy sections were used "
        "for this claim analysis."
    )

    for index, document in enumerate(
        retrieved_documents,
        start=1,
    ):
        metadata = getattr(document, "metadata", {}) or {}

        file_name = (
            metadata.get("file_name")
            or metadata.get("filename")
            or metadata.get("source")
            or "Policy Document"
        )

        source = metadata.get(
            "source",
            "Source path not available",
        )

        page_content = getattr(
            document,
            "page_content",
            str(document),
        )

        with st.expander(
            f"📄 Source {index}: {file_name}",
            expanded=False,
        ):
            st.caption(f"Source: {source}")
            st.write(page_content)


def initialize_session_state() -> None:
    """
    Create session-state variables.
    """

    if "claim_history" not in st.session_state:
        st.session_state.claim_history = []

    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "New Claim"


def save_claim_to_history(final_state: dict) -> None:
    """
    Save the completed claim in temporary session history.
    """

    claim_record = {
        "customer_name": final_state.get(
            "customer_name",
            "Not Available",
        ),
        "policy_number": final_state.get(
            "policy_number",
            "Not Available",
        ),
        "incident_type": final_state.get(
            "incident_type",
            "Not Available",
        ),
        "claim_amount": final_state.get(
            "claim_amount",
            0,
        ),
        "coverage_status": final_state.get(
            "coverage_status",
            "unclear",
        ),
        "final_decision": final_state.get(
            "final_decision",
            "manual_review_required",
        ),
        "confidence": normalize_confidence(
            final_state.get("confidence", 0)
        ),
    }

    st.session_state.claim_history.append(claim_record)


initialize_session_state()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🛡️ ClaimGuard AI")

    st.caption(
        "Insurance Claims Adjudication Agent"
    )

    st.divider()

    selected_page = st.radio(
        "Navigation",
        options=[
            "New Claim",
            "Claim History",
            "Policy Documents",
            "Dashboard",
            "Reports",
            "Settings",
        ],
        format_func=lambda page: {
            "New Claim": "📄 New Claim",
            "Claim History": "🕘 Claim History",
            "Policy Documents": "📁 Policy Documents",
            "Dashboard": "📊 Dashboard",
            "Reports": "📋 Reports",
            "Settings": "⚙️ Settings",
        }[page],
        key="selected_page",
        label_visibility="collapsed",
    )

    st.divider()

    with st.container(border=True):

        st.subheader("🎧 Need Help?")

        st.write(
            "Contact the claims support team for assistance."
        )

        st.button(
            "Contact Support",
            use_container_width=True,
            disabled=True,
        )

    st.divider()

    st.subheader("👤 Adjuster")

    st.caption("Claims Adjuster")

    st.divider()

    st.caption("🛡️ Version 1.0.0")


# =========================================================
# NEW CLAIM PAGE
# =========================================================

if selected_page == "New Claim":

    header_column, status_column = st.columns(
        [5, 1.3],
        gap="large",
    )

    with header_column:

        st.title("Insurance Claims Adjudication")

        st.write(
            "Submit a motor insurance claim and receive an "
            "AI-assisted coverage analysis based on the available "
            "policy documents."
        )

    with status_column:

        with st.container(border=True):

            st.success("● Online")

            st.caption("Application Status")

    st.divider()

    # -----------------------------------------------------
    # NEW CLAIM FORM
    # -----------------------------------------------------

    with st.container(border=True):

        title_icon, title_content = st.columns(
            [0.7, 10],
            vertical_alignment="center",
        )

        with title_icon:
            st.subheader("📄")

        with title_content:
            st.subheader("New Claim")
            st.caption(
                "Enter the customer, policy and incident details below."
            )

        st.write("")

        with st.form(
            "claim_form",
            clear_on_submit=False,
        ):

            customer_column, policy_column = st.columns(
                2,
                gap="large",
            )

            with customer_column:

                customer_name = st.text_input(
                    "Customer Name *",
                    placeholder="Example: Satish Salunkhe",
                )

            with policy_column:

                policy_number = st.text_input(
                    "Policy Number *",
                    placeholder="Example: POL-1001",
                )

            incident_column, amount_column = st.columns(
                2,
                gap="large",
            )

            with incident_column:

                incident_type = st.selectbox(
                    "Incident Type *",
                    options=[
                        "Select Incident Type",
                        "Accident Damage",
                        "Flood Damage",
                        "Theft",
                        "Fire Damage",
                        "Engine Damage",
                        "Natural Disaster",
                        "Third-Party Damage",
                        "Other",
                    ],
                )

            with amount_column:

                claim_amount = st.number_input(
                    "Claim Amount (₹) *",
                    min_value=0.0,
                    step=1000.0,
                    format="%.2f",
                )

            incident_description = st.text_area(
                "Incident Description *",
                placeholder=(
                    "Describe what happened, where it happened "
                    "and how the vehicle was damaged."
                ),
                height=140,
            )

            confirm_details = st.checkbox(
                "I confirm that the entered claim details are correct."
            )

            submitted = st.form_submit_button(
                "🔍 Analyze Claim",
                type="primary",
                use_container_width=True,
            )

    st.write("")

    # -----------------------------------------------------
    # HOW IT WORKS
    # -----------------------------------------------------

    with st.container(border=True):

        workflow_title_column, workflow_text_column = st.columns(
            [0.7, 10],
            vertical_alignment="center",
        )

        with workflow_title_column:
            st.subheader("✨")

        with workflow_text_column:
            st.subheader("How It Works")

        st.write("")

        step1, step2, step3, step4, step5 = st.columns(
            5,
            gap="medium",
        )

        with step1:

            with st.container(border=True):
                st.subheader("📄")
                st.markdown("**1. Submit Claim**")
                st.caption(
                    "Provide claim and incident details."
                )

        with step2:

            with st.container(border=True):
                st.subheader("🔍")
                st.markdown("**2. Retrieve Policies**")
                st.caption(
                    "AI retrieves relevant policy clauses."
                )

        with step3:

            with st.container(border=True):
                st.subheader("🧠")
                st.markdown("**3. Analyze Coverage**")
                st.caption(
                    "AI checks coverage using retrieved data."
                )

        with step4:

            with st.container(border=True):
                st.subheader("⚖️")
                st.markdown("**4. Make Decision**")
                st.caption(
                    "AI generates a final decision."
                )

        with step5:

            with st.container(border=True):
                st.subheader("📋")
                st.markdown("**5. View Result**")
                st.caption(
                    "Review the result and policy sources."
                )

    # -----------------------------------------------------
    # CLAIM PROCESSING
    # -----------------------------------------------------

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

        if incident_type == "Select Incident Type":
            validation_errors.append(
                "Please select an incident type."
            )

        if claim_amount <= 0:
            validation_errors.append(
                "Claim amount must be greater than zero."
            )

        if not incident_description.strip():
            validation_errors.append(
                "Incident description is required."
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
                st.write(f"• {validation_error}")

        else:

            initial_state: ClaimState = {
                "policy_number": policy_number.strip(),
                "customer_name": customer_name.strip(),
                "incident_type": incident_type,
                "incident_description": (
                    incident_description.strip()
                ),
                "claim_amount": float(claim_amount),
            }

            try:

                st.write("")

                with st.status(
                    "Processing insurance claim...",
                    expanded=True,
                ) as processing_status:

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

                    processing_status.update(
                        label="Claim processing completed",
                        state="complete",
                        expanded=False,
                    )

                final_decision = final_state.get(
                    "final_decision",
                    "manual_review_required",
                )

                coverage_status = final_state.get(
                    "coverage_status",
                    "unclear",
                )

                confidence = normalize_confidence(
                    final_state.get(
                        "confidence",
                        0,
                    )
                )

                retrieved_documents = final_state.get(
                    "retrieved_documents",
                    [],
                )

                save_claim_to_history(final_state)

                st.write("")

                # ---------------------------------------------
                # RESULT SECTION
                # ---------------------------------------------

                with st.container(border=True):

                    result_icon, result_title = st.columns(
                        [0.7, 10],
                        vertical_alignment="center",
                    )

                    with result_icon:
                        st.subheader("⚖️")

                    with result_title:
                        st.subheader("Claim Analysis Result")
                        st.caption(
                            "AI-assisted decision with supporting "
                            "policy evidence."
                        )

                    st.write("")

                    show_decision_status(
                        final_decision
                    )

                    metric1, metric2, metric3 = st.columns(
                        3,
                        gap="large",
                    )

                    with metric1:

                        st.metric(
                            "Final Decision",
                            format_status(
                                final_decision
                            ),
                        )

                    with metric2:

                        st.metric(
                            "Coverage Status",
                            format_status(
                                coverage_status
                            ),
                        )

                    with metric3:

                        st.metric(
                            "Confidence",
                            f"{confidence * 100:.0f}%",
                        )

                    st.progress(confidence)

                    st.divider()

                    st.subheader("Claim Summary")

                    summary1, summary2 = st.columns(
                        2,
                        gap="large",
                    )

                    with summary1:

                        st.text_input(
                            "Customer Name",
                            value=final_state.get(
                                "customer_name",
                                customer_name,
                            ),
                            disabled=True,
                            key="result_customer_name",
                        )

                        st.text_input(
                            "Incident Type",
                            value=final_state.get(
                                "incident_type",
                                incident_type,
                            ),
                            disabled=True,
                            key="result_incident_type",
                        )

                    with summary2:

                        st.text_input(
                            "Policy Number",
                            value=final_state.get(
                                "policy_number",
                                policy_number,
                            ),
                            disabled=True,
                            key="result_policy_number",
                        )

                        result_amount = final_state.get(
                            "claim_amount",
                            claim_amount,
                        )

                        st.text_input(
                            "Claim Amount",
                            value=f"₹{float(result_amount):,.2f}",
                            disabled=True,
                            key="result_claim_amount",
                        )

                    analysis_tab, decision_tab, sources_tab = st.tabs(
                        [
                            "Coverage Analysis",
                            "Final Decision",
                            "Policy Sources",
                        ]
                    )

                    with analysis_tab:

                        st.subheader(
                            "Coverage Analysis"
                        )

                        st.write(
                            final_state.get(
                                "coverage_reason",
                                "Coverage reason is not available.",
                            )
                        )

                    with decision_tab:

                        st.subheader(
                            "Final Decision"
                        )

                        st.write(
                            "**Decision:** "
                            f"{format_status(final_decision)}"
                        )

                        st.write(
                            "**Reason:** "
                            f"{final_state.get(
                                'final_reason',
                                'Final reason is not available.'
                            )}"
                        )

                        st.write(
                            "**Confidence:** "
                            f"{confidence * 100:.0f}%"
                        )

                    with sources_tab:

                        st.subheader(
                            "Retrieved Policy Documents"
                        )

                        show_policy_sources(
                            retrieved_documents
                        )

            except Exception as error:

                st.error(
                    "The claim analysis could not be completed."
                )

                st.warning(
                    "Check the API key, vector database, "
                    "dependencies and terminal logs."
                )

                with st.expander(
                    "View Technical Error",
                    expanded=False,
                ):
                    st.exception(error)


# =========================================================
# CLAIM HISTORY PAGE
# =========================================================

elif selected_page == "Claim History":

    st.title("Claim History")

    st.write(
        "View claims analyzed during the current application session."
    )

    st.divider()

    if not st.session_state.claim_history:

        st.info(
            "No claim history is available. "
            "Analyze a claim first."
        )

    else:

        search_text = st.text_input(
            "Search claims",
            placeholder=(
                "Search by customer name or policy number"
            ),
        )

        decision_filter = st.selectbox(
            "Filter by Decision",
            options=[
                "All Decisions",
                "Approved",
                "Claim Not Covered",
                "Manual Review Required",
            ],
        )

        filtered_claims = []

        for claim in st.session_state.claim_history:

            customer_value = str(
                claim.get("customer_name", "")
            ).lower()

            policy_value = str(
                claim.get("policy_number", "")
            ).lower()

            search_matches = (
                not search_text
                or search_text.lower() in customer_value
                or search_text.lower() in policy_value
            )

            formatted_decision = format_status(
                claim.get("final_decision", "")
            )

            decision_matches = (
                decision_filter == "All Decisions"
                or formatted_decision == decision_filter
            )

            if search_matches and decision_matches:
                filtered_claims.append(claim)

        if not filtered_claims:

            st.warning(
                "No claims match the selected search or filter."
            )

        else:

            history_rows = []

            for index, claim in enumerate(
                filtered_claims,
                start=1,
            ):
                history_rows.append(
                    {
                        "Claim No.": index,
                        "Customer": claim.get(
                            "customer_name",
                            "Not Available",
                        ),
                        "Policy Number": claim.get(
                            "policy_number",
                            "Not Available",
                        ),
                        "Incident": claim.get(
                            "incident_type",
                            "Not Available",
                        ),
                        "Amount": (
                            f"₹{float(
                                claim.get('claim_amount', 0)
                            ):,.2f}"
                        ),
                        "Decision": format_status(
                            claim.get(
                                "final_decision",
                                "",
                            )
                        ),
                        "Confidence": (
                            f"{claim.get(
                                'confidence',
                                0
                            ) * 100:.0f}%"
                        ),
                    }
                )

            st.dataframe(
                history_rows,
                use_container_width=True,
                hide_index=True,
            )

            if st.button(
                "Clear Claim History",
                type="secondary",
            ):
                st.session_state.claim_history = []
                st.rerun()


# =========================================================
# POLICY DOCUMENTS PAGE
# =========================================================

elif selected_page == "Policy Documents":

    st.title("Policy Documents")

    st.write(
        "Policy documents used by the RAG retrieval system."
    )

    st.divider()

    st.info(
        "The policy document management page will be added "
        "in the next development step."
    )

    with st.container(border=True):

        st.subheader("📁 Available Document Types")

        st.write("• Motor insurance policy")

        st.write("• Policy endorsements")

        st.write("• Coverage exclusions")

        st.write("• State insurance regulations")


# =========================================================
# DASHBOARD PAGE
# =========================================================

elif selected_page == "Dashboard":

    st.title("Claims Dashboard")

    st.write(
        "Summary of claims analyzed during this session."
    )

    st.divider()

    history = st.session_state.claim_history

    total_claims = len(history)

    approved_claims = sum(
        1
        for claim in history
        if claim.get("final_decision") == "approved"
    )

    not_covered_claims = sum(
        1
        for claim in history
        if claim.get("final_decision")
        in ["claim_not_covered", "denied"]
    )

    manual_review_claims = sum(
        1
        for claim in history
        if claim.get("final_decision")
        not in [
            "approved",
            "claim_not_covered",
            "denied",
        ]
    )

    metric1, metric2, metric3, metric4 = st.columns(
        4,
        gap="large",
    )

    with metric1:
        st.metric(
            "Total Claims",
            total_claims,
        )

    with metric2:
        st.metric(
            "Approved",
            approved_claims,
        )

    with metric3:
        st.metric(
            "Not Covered",
            not_covered_claims,
        )

    with metric4:
        st.metric(
            "Manual Review",
            manual_review_claims,
        )

    if total_claims == 0:
        st.info(
            "No dashboard data is available. "
            "Analyze a claim first."
        )


# =========================================================
# REPORTS PAGE
# =========================================================

elif selected_page == "Reports":

    st.title("Reports")

    st.write(
        "Generate and download insurance claim reports."
    )

    st.divider()

    st.info(
        "PDF and Excel report functionality can be added later."
    )


# =========================================================
# SETTINGS PAGE
# =========================================================

elif selected_page == "Settings":

    st.title("Settings")

    st.write(
        "Application and claims-processing settings."
    )

    st.divider()

    with st.container(border=True):

        st.subheader("Application Information")

        st.text_input(
            "Application Name",
            value="ClaimGuard AI",
            disabled=True,
        )

        st.text_input(
            "Version",
            value="1.0.0",
            disabled=True,
        )

        st.selectbox(
            "Default Decision Mode",
            options=[
                "AI Assisted",
                "Manual Review",
            ],
            disabled=True,
        )


# =========================================================
# FOOTER
# =========================================================

st.write("")
st.divider()

st.caption(
    "ClaimGuard AI is an AI-assisted demonstration application. "
    "Final insurance decisions must be reviewed by an authorized "
    "insurance professional."
)