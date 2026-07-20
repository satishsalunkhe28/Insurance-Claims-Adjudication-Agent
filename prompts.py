# Prompt for coverage analysis

COVERAGE_ANALYSIS_PROMPT = """
You are an insurance claim analyst.

Analyze the customer claim using ONLY the retrieved policy documents.

Customer Details

Policy Number:
{policy_number}

Incident Type:
{incident_type}

Incident Description:
{incident_description}

Claim Amount:
{claim_amount}

Retrieved Policy Documents

{policy_context}

Determine:

1. coverage_status
2. coverage_reason
"""


# Prompt for final decision

FINAL_DECISION_PROMPT = """
You are a senior insurance claims adjudication officer.

Coverage Status:
{coverage_status}

Coverage Reason:
{coverage_reason}

Decision Rules

covered
→ approved

not_covered
→ claim_not_covered

unclear
→ manual_review_required

Return:

1. final_decision
2. final_reason
3. confidence
"""


if __name__ == "__main__":

    print("Coverage Prompt")
    print(COVERAGE_ANALYSIS_PROMPT)

    print("\n" + "=" * 60 + "\n")

    print("Decision Prompt")
    print(FINAL_DECISION_PROMPT)