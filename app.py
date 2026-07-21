import streamlit as st

from graph import claim_graph
from llm import create_llm
from state import ClaimState


st.set_page_config(
    page_title="ClaimGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# ENTERPRISE UI
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    :root {
        --navy: #12355B;
        --navy-hover: #0B2745;
        --blue: #1F5F99;
        --surface: #151A22;
        --border: #303846;
    }

    .stApp {
        background: #0E131B;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        background: var(--navy) !important;
        border: 1px solid #2C5E8F !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 650 !important;
        min-height: 48px !important;
        box-shadow: none !important;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        background: var(--navy-hover) !important;
        border-color: #4B82B6 !important;
        color: white !important;
    }

    div.stButton > button:focus,
    div.stFormSubmitButton > button:focus {
        box-shadow: 0 0 0 3px rgba(31, 95, 153, 0.28) !important;
    }

    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 16px;
    }

    [data-testid="stForm"] {
        background: #121821;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
    }

    .decision-card {
        border-radius: 10px;
        padding: 18px 20px;
        font-size: 18px;
        font-weight: 700;
        margin: 8px 0 20px 0;
    }

    .approved-card {
        background: rgba(25, 135, 84, 0.17);
        border: 1px solid rgba(46, 204, 113, 0.55);
        color: #73E2A7;
    }

    .denied-card {
        background: rgba(180, 45, 55, 0.17);
        border: 1px solid rgba(225, 83, 97, 0.55);
        color: #FF8E99;
    }

    .review-card {
        background: rgba(176, 126, 16, 0.18);
        border: 1px solid rgba(240, 185, 55, 0.55);
        color: #FFD36A;
    }

    .explanation-card {
        background: #141D28;
        border: 1px solid #30465E;
        border-left: 4px solid #2F75B5;
        border-radius: 9px;
        padding: 20px;
        line-height: 1.7;
        margin-top: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def display_name(value: str) -> str:
    if not value:
        return "Not Available"
    return value.replace("_", " ").title()


@st.cache_resource
def application_health():
    try:
        create_llm()
        return True, "Groq LLM connection is configured."
    except Exception as error:
        return False, str(error)


def show_application_status():
    online, message = application_health()

    if online:
        st.success("● Application Online")
    else:
        st.error("● Application Offline")
        with st.expander("Status details"):
            st.write(message)


def show_decision_card(decision: str):
    normalized = (decision or "").strip().lower()

    if normalized == "approved":
        css_class = "approved-card"
        text = "✓ Claim Approved"
    elif normalized == "claim_not_covered":
        css_class = "denied-card"
        text = "✕ Claim Not Covered"
    else:
        css_class = "review-card"
        text = "⚠ Manual Review Required"

    st.markdown(
        f'<div class="decision-card {css_class}">{text}</div>',
        unsafe_allow_html=True,
    )


def show_explanation(text: str):
    safe_text = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )

    st.markdown(
        f'<div class="explanation-card">{safe_text}</div>',
        unsafe_allow_html=True,
    )


def show_policy_sources(documents):
    if not documents:
        st.info("No relevant policy documents were retrieved.")
        return

    st.caption(
        f"{len(documents)} policy sections were used "
        "for this claim analysis."
    )

    for index, document in enumerate(documents, start=1):
        file_name = document.metadata.get(
            "file_name",
            "Unknown Source",
        )
        source = document.metadata.get(
            "source",
            "Source path not available",
        )

        with st.expander(
            f"Source {index}: {file_name}"
        ):
            st.caption(f"Source: {source}")
            st.write(document.page_content)


with st.sidebar:
    st.title("🛡️ ClaimGuard AI")
    st.caption("Insurance Claims Adjudication Agent")
    st.divider()
    st.button(
        "New Claim",
        use_container_width=True,
    )
    st.button(
        "Claim History",
        use_container_width=True,
        disabled=True,
    )
    st.button(
        "Policy Documents",
        use_container_width=True,
        disabled=True,
    )
    st.divider()
    st.caption("Version 1.1")


header, health = st.columns([4, 1])

with header:
    st.title("Insurance Claims Adjudication")
    st.write(
        "Submit a private motor claim for a grounded, "
        "AI-assisted policy assessment."
    )

with health:
    show_application_status()

st.divider()
st.subheader("New Claim")

with st.form("claim_form"):
    left, right = st.columns(2)

    with left:
        customer_name = st.text_input(
            "Customer Name *",
            placeholder="Example: Rahul Sharma",
        )

    with right:
        policy_number = st.text_input(
            "Policy Number *",
            placeholder="Example: POL-1001",
        )

    incident_col, amount_col = st.columns([2, 1])

    with incident_col:
        incident_type = st.selectbox(
            "Incident Type *",
            [
                "Road Accident",
                "Flood Damage",
                "Theft",
                "Fire Damage",
                "Engine Damage",
                "Natural Disaster",
                "Third-Party Damage",
                "Other",
            ],
        )

    with amount_col:
        claim_amount = st.number_input(
            "Claim Amount ₹ *",
            min_value=0.0,
            step=1000.0,
            format="%.2f",
        )

    incident_description = st.text_area(
        "Incident Description *",
        placeholder=(
            "Explain what happened, the damage caused, "
            "and any relevant documents or circumstances."
        ),
        height=150,
    )

    confirmed = st.checkbox(
        "I confirm that the entered claim details are correct."
    )

    submitted = st.form_submit_button(
        "Analyze Claim",
        type="primary",
        use_container_width=True,
    )


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
    if not confirmed:
        errors.append(
            "Please confirm the claim details."
        )

    if errors:
        st.error("Please correct the following:")
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
            "claim_amount": float(claim_amount),
        }

        try:
            with st.status(
                "Analyzing claim...",
                expanded=True,
            ) as status:
                st.write("Retrieving relevant policy sections...")
                final_state = claim_graph.invoke(initial_state)
                st.write("Applying policy coverage rules...")
                st.write("Preparing the final explanation...")
                status.update(
                    label="Claim analysis completed",
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
            confidence = float(
                final_state.get(
                    "confidence",
                    0,
                )
            )

            st.divider()
            st.subheader("Claim Result")
            show_decision_card(final_decision)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Final Decision",
                    display_name(final_decision),
                )
            with col2:
                st.metric(
                    "Coverage Status",
                    display_name(coverage_status),
                )
            with col3:
                st.metric(
                    "Confidence",
                    f"{confidence * 100:.0f}%",
                )

            st.progress(
                min(max(confidence, 0.0), 1.0)
            )

            analysis_tab, decision_tab, sources_tab = st.tabs(
                [
                    "Coverage Analysis",
                    "Final Decision",
                    "Policy Sources",
                ]
            )

            with analysis_tab:
                st.subheader("Coverage Analysis")
                st.markdown("#### Detailed assessment")
                show_explanation(
                    final_state.get(
                        "coverage_reason",
                        "No explanation is available.",
                    )
                )

                st.markdown("#### Policy basis")
                st.write(
                    final_state.get(
                        "policy_basis",
                        "Policy basis is unavailable.",
                    )
                )

                st.markdown("#### Recommended next step")
                st.write(
                    final_state.get(
                        "recommendation",
                        "Refer the claim for review.",
                    )
                )

            with decision_tab:
                st.subheader("Final Decision")
                show_decision_card(final_decision)
                st.markdown("#### Decision explanation")
                show_explanation(
                    final_state.get(
                        "final_reason",
                        "No final explanation is available.",
                    )
                )
                st.markdown("#### Confidence")
                st.write(f"{confidence * 100:.0f}%")
                st.progress(
                    min(max(confidence, 0.0), 1.0)
                )

            with sources_tab:
                st.subheader(
                    "Retrieved Policy Documents"
                )
                show_policy_sources(
                    final_state.get(
                        "retrieved_documents",
                        [],
                    )
                )

        except Exception as error:
            st.error(
                "The claim analysis could not be completed."
            )
            st.warning(
                "Check the API key, vector database, "
                "and Streamlit logs."
            )
            with st.expander("Technical details"):
                st.exception(error)


st.divider()
st.caption(
    "ClaimGuard AI is a demonstration application. "
    "Final decisions should be verified by an authorized adjuster."
)