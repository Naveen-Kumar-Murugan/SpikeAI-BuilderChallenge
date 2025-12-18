import json
from app.llm.client import ask_llm
from app.services.ga4_service import run_ga4_query

SYSTEM_PROMPT = """
You are a Google Analytics 4 query planner.

Task:
Convert a natural language question into a GA4 Data API query plan.

Rules (STRICT):
- Respond with ONLY valid JSON
- Do NOT include explanations
- Do NOT include markdown or code fences
- Output must be parseable by json.loads()

Required fields:
- metrics: list of GA4 metric names
- dimensions: list of GA4 dimension names
- dateRanges: list with startDate and endDate

Optional fields (include ONLY if relevant):
- dimensionFilter
- metricFilter
- orderBys
- limit
- offset
- keepEmptyRows
- currencyCode
- cohortSpec
- aggregations

Guidelines:
- Use official GA4 Data API field names
- Prefer minimal queries
- Infer reasonable date ranges when not specified
"""

# def handle_analytics_query(query, property_id):
#     print("Generating GA4 query plan...")
#     plan_json = ask_llm(
#         SYSTEM_PROMPT,
#         f"Question: {query}"
#     )
#     print(f"Received plan JSON: {plan_json}")
#     plan = json.loads(plan_json)
#     print(f"Generated plan: {plan}")
#     data = run_ga4_query(plan, property_id)
#     print(f"GA4 query result: {data}")
#     return {
#         "plan": plan,
#         "result": data
#     }


def _extract_json(text: str):
    """
    Extracts the first JSON object from a string.
    Fallback for when the LLM adds extra text.
    """
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in LLM response")
    return json.loads(match.group())

def handle_analytics_query(query, property_id):
    print("Generating GA4 query plan...")

    plan_json = ask_llm(
        SYSTEM_PROMPT,
        f"Question: {query}"
    )

    print("Raw LLM response:")
    print(repr(plan_json))  # shows whitespace / newlines

    if not plan_json or not plan_json.strip():
        raise ValueError("LLM returned empty response")

    # Try strict parse first
    try:
        plan = json.loads(plan_json)
    except json.JSONDecodeError:
        print("Strict JSON parse failed, attempting extraction...")
        plan = _extract_json(plan_json)

    print(f"Generated plan: {plan}")

    data = run_ga4_query(plan, property_id)
    print(f"GA4 query result: {data}")

    return {
        "plan": plan,
        "result": data
    }