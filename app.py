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
# APPLICATION STYLING
# =========================================================

st.markdown(
    """
    <style>

    /* ---------------------------------
       MAIN APPLICATION
    --------------------------------- */

    .stApp {
        background-color: #EEF4FF;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    [data-testid="stMain"] {
        background-color: #EEF4FF;
    }

    [data-testid="stMain"] h1 {
        color: #143A73 !important;
        font-weight: 800 !important;
        letter-spacing: -1px;
    }

    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3 {
        color: #17437D !important;
        font-weight: 700 !important;
    }

    [data-testid="stMain"] p {
        color: #415A77;
    }

    /* ---------------------------------
       SIDEBAR
    --------------------------------- */

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #063A91 0%,
            #0A5BDE 55%,
            #063A91 100%
        );
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.3rem;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.22);
    }

    [data-testid="stSidebar"] .stButton button {
        width: 100%;
        min-height: 46px;
        border-radius: 9px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        background-color: rgba(255, 255, 255, 0.09);
        color: #FFFFFF !important;
        text-align: left;
        font-weight: 600;
        transition: 0.2s ease;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background-color: rgba(255, 255, 255, 0.20);
        border-color: rgba(255, 255, 255, 0.35);
    }

    [data-testid="stSidebar"] .stButton:first-of-type button {
        background-color: #FFFFFF;
        color: #0A5BDE !important;
        border: none;
    }

    /* ---------------------------------
       CARDS
    --------------------------------- */

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border: 1px solid #D8E4F3;
        border-radius: 16px;
        box-shadow: 0 8px 20px rgba(27, 67, 133, 0.08);
    }

    [data-testid="stVerticalBlockBorderWrapper"] h1,
    [data-testid="stVerticalBlockBorderWrapper"] h2,
    [data-testid="stVerticalBlockBorderWrapper"] h3 {
        color: #17437D !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] p {
        color: #415A77 !important;
    }

    /* ---------------------------------
       FORM LABELS
    --------------------------------- */

    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stNumberInput label,
    .stCheckbox label {
        color: #17365F !important;
        font-weight: 600 !important;
    }

    /* ---------------------------------
       INPUT CONTROLS
    --------------------------------- */

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #17365F !important;
        border: 1px solid #D6E2F2 !important;
        border-radius: 10px !important;
    }

    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus {
        border-color: #0A5BDE !important;
        box-shadow: 0 0 0 2px rgba(10, 91, 222, 0.12) !important;
    }

    [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #17365F !important;
        border: 1px solid #D6E2F2 !important;
        border-radius: 10px !important;
    }

    /* ---------------------------------
       ANALYZE BUTTON
    --------------------------------- */

    div[data-testid="stFormSubmitButton"] button {
        width: 100%;
        min-height: 50px;
        background-color: #0A5BDE;
        color: #FFFFFF !important;
        border: none;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 700;
        box-shadow: 0 8px 18px rgba(10, 91, 222, 0.20);
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #0849B2;
        color: #FFFFFF !important;
    }

    /* ---------------------------------
       METRIC CARDS
    --------------------------------- */

    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #D8E4F3;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 5px 14px rgba(27, 67, 133, 0.06);
    }

    [data-testid="stMetricLabel"] {
        color: #5A6F8D !important;
    }

    [data-testid="stMetricValue"] {
        color: #143A73 !important;
        font-size: 22px !important;
    }

    /* ---------------------------------
       TABS
    --------------------------------- */

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #E8F0FD;
        border-radius: 8px 8px 0 0;
        padding: 10px 18px;
        color: #17437D;
    }

    .stTabs [aria-selected="true"] {
        background-color: #0A5BDE !important;
        color: #FFFFFF !important;
    }

    /* ---------------------------------
       EXPANDERS
    --------------------------------- */

    [data-testid="stExpander"] {
        background-color: #FFFFFF;
        border: 1px solid #D8E4F3;
        border-radius: 10px;
    }

    /* ---------------------------------
       PROGRESS BAR
    --------------------------------- */

    .stProgress > div > div > div > div {
        background-color: #0A5BDE;
    }

    /* ---------------------------------
       HIDE DEFAULT STREAMLIT ITEMS
    --------------------------------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def format_status(value: str) -> str:
    """Convert underscore-separated values into readable text."""

    if not value:
        return "Not Available"

    return value.replace("_", " ").title()


def normalize_confidence(value) -> float:
    """Convert confidence into a number between 0 and 1."""

    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.0

    if confidence > 1:
        confidence = confidence / 100

    return min(max(confidence, 0.0), 1.0)


def show_decision(final_decision: str) -> None:
    """Display the final claim decision."""

    if final_decision == "approved":
        st.success("✅ Claim Approved")

    elif final_decision == "claim_not_covered":
        st.error("❌ Claim Not Covered")

    else:
        st.warning("⚠️ Manual Review Required")


def show_policy_sources(documents) -> None:
    """Display policy documents retrieved by the RAG system."""

    if not documents:
        st.info("No relevant policy documents were retrieved.")
        return

    st.caption(
        f"{len(documents)} policy sections were used "
        "during this claim analysis."
    )

    for index, document in enumerate(documents, start=1):

        metadata = getattr(document, "metadata", {}) or {}

        file_name = (
            metadata.get("file_name")
            or metadata.get("filename")
            or metadata.get("source")
            or "Policy Document"
        )

        source = metadata.get(
            "source",
            "Source not available",
        )

        content = getattr(
            document,
            "page_content",
            str(document),
        )

        with st.expander(
            f"Source {index}: {file_name}",
            expanded=False,
        ):
            st.caption(f"Source: {source}")
            st.write(content)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        "<div style='text-align:center;font-size:65px;'>🛡️</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <h2 style="
            text-align:center;
            margin-top:-10px;
            margin-bottom:5px;
            color:white;
        ">
            ClaimGuard AI
        </h2>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <p style="
            text-align:center;
            color:#D9E7FF;
            font-size:14px;
            line-height:1.5;
        ">
            Insurance Claims<br>
            Adjudication Agent
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.button(
        "📄  New Claim",
        use_container_width=True,
    )

    st.button(
        "📑  Claim History",
        use_container_width=True,
        disabled=True,
    )

    st.button(
        "📚  Policy Documents",
        use_container_width=True,
        disabled=True,
    )

    st.button(
        "📊  Dashboard",
        use_container_width=True,
        disabled=True,
    )

    st.button(
        "📋  Reports",
        use_container_width=True,
        disabled=True,
    )

    st.divider()

    with st.container(border=True):

        st.markdown("#### 🎧 Need Help?")

        st.caption(
            "Contact the claims support team."
        )

    st.write("")

    user_icon, user_details = st.columns(
        [1, 3]
    )

    with user_icon:
        st.markdown("### 👤")

    with user_details:
        st.markdown("**Claims Adjuster**")
        st.caption("Authorized User")

    st.divider()

    st.caption("🛡️ Version 1.0.0")


# =========================================================
# MAIN HEADER
# =========================================================

header_column, status_column = st.columns(
    [5, 1.3],
    gap="large",
)

with header_column:

    st.title("Insurance Claims Adjudication")

    st.markdown(
        """
        <p style="
            color:#415A77;
            font-size:17px;
            line-height:1.6;
            font-weight:500;
            margin-top:-5px;
        ">
            Submit a motor insurance claim and receive an
            AI-assisted coverage analysis based on the available
            policy documents.
        </p>
        """,
        unsafe_allow_html=True,
    )

with status_column:

    with st.container(border=True):

        st.success("● Online")

        st.caption("Application Status")


st.write("")


# =========================================================
# CLAIM FORM
# =========================================================

with st.container(border=True):

    heading_icon, heading_text = st.columns(
        [0.7, 9]
    )

    with heading_icon:
        st.markdown("## 📄")

    with heading_text:
        st.subheader("New Claim")

        st.caption(
            "Enter the customer, policy and incident details below."
        )

    st.write("")

    with st.form(
        "claim_form",
        clear_on_submit=False,
        border=False,
    ):

        customer_column, policy_column = st.columns(
            2,
            gap="large",
        )

        with customer_column:

            customer_name = st.text_input(
                "Customer Name *",
                placeholder="Example: Rahul Sharma",
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
                "Describe what happened, where it happened, "
                "and how the vehicle was damaged."
            ),
            height=130,
        )

        confirm_details = st.checkbox(
            "I confirm that the entered claim details are correct."
        )

        submitted = st.form_submit_button(
            "🔍  Analyze Claim",
            type="primary",
            use_container_width=True,
        )


# =========================================================
# HOW IT WORKS
# =========================================================

st.write("")

with st.container(border=True):

    workflow_icon, workflow_heading = st.columns(
        [0.7, 9]
    )

    with workflow_icon:
        st.markdown("## ✨")

    with workflow_heading:
        st.subheader("How It Works")

    st.write("")

    step1, step2, step3, step4, step5 = st.columns(
        5,
        gap="medium",
    )

    with step1:
        st.markdown("### 📄")
        st.markdown("**1. Submit Claim**")
        st.caption(
            "Provide customer and incident details."
        )

    with step2:
        st.markdown("### 🔍")
        st.markdown("**2. Retrieve Policies**")
        st.caption(
            "Retrieve relevant policy clauses."
        )

    with step3:
        st.markdown("### 🧠")
        st.markdown("**3. Analyze Coverage**")
        st.caption(
            "Check coverage using retrieved data."
        )

    with step4:
        st.markdown("### ⚖️")
        st.markdown("**4. Make Decision**")
        st.caption(
            "Generate the final claim decision."
        )

    with step5:
        st.markdown("### 📋")
        st.markdown("**5. View Report**")
        st.caption(
            "Review the decision and policy sources."
        )


# =========================================================
# CLAIM PROCESSING
# =========================================================

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
            "Please confirm that the entered claim details are correct."
        )

    if validation_errors:

        st.write("")

        st.error(
            "Please correct the following information:"
        )

        for error_message in validation_errors:
            st.write(f"• {error_message}")

    else:

        initial_state: ClaimState = {
            "policy_number": policy_number.strip(),
            "customer_name": customer_name.strip(),
            "incident_type": incident_type,
            "incident_description": incident_description.strip(),
            "claim_amount": float(claim_amount),
        }

        try:

            st.write("")

            with st.status(
                "Processing insurance claim...",
                expanded=True,
            ) as processing_status:

                st.write(
                    "📄 Claim information received."
                )

                st.write(
                    "🔍 Retrieving relevant policy documents."
                )

                final_state = claim_graph.invoke(
                    initial_state
                )

                st.write(
                    "🧠 Coverage analysis completed."
                )

                st.write(
                    "⚖️ Final decision generated."
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

            coverage_reason = final_state.get(
                "coverage_reason",
                "Coverage analysis is not available.",
            )

            final_reason = final_state.get(
                "final_reason",
                "Final decision reason is not available.",
            )

            retrieved_documents = final_state.get(
                "retrieved_documents",
                [],
            )

            st.write("")

            with st.container(border=True):

                result_icon, result_heading = st.columns(
                    [0.7, 9]
                )

                with result_icon:
                    st.markdown("## ⚖️")

                with result_heading:
                    st.subheader(
                        "Claim Analysis Result"
                    )

                    st.caption(
                        "AI-assisted claim decision and "
                        "supporting policy evidence."
                    )

                st.write("")

                show_decision(
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

                st.progress(
                    confidence
                )

                st.write("")

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
                        coverage_reason
                    )

                with decision_tab:

                    st.subheader(
                        "Final Decision"
                    )

                    st.write(
                        f"**Decision:** "
                        f"{format_status(final_decision)}"
                    )

                    st.write(
                        f"**Reason:** {final_reason}"
                    )

                    st.write(
                        f"**Confidence:** "
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

            st.write("")

            st.error(
                "The claim analysis could not be completed."
            )

            st.warning(
                "Check the Groq API key, vector database, "
                "installed dependencies and terminal logs."
            )

            with st.expander(
                "View Technical Error",
                expanded=False,
            ):
                st.exception(error)


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