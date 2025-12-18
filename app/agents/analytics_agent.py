import json
import re
import os
from app.llm.client import ask_llm
from app.services.ga4_service import run_ga4_query

def load_allowed_fields(path="ga4_allowed_fields.txt"):
    """
    Loads allowed GA4 metrics and dimensions from a text file.
    """
    metrics = set()
    dimensions = set()
    current = None

    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found. Please provide allowed GA4 fields file.")

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                if "metric" in line.lower():
                    current = "metric"
                elif "dimension" in line.lower():
                    current = "dimension"
                continue

            if current == "metric":
                metrics.add(line)
            elif current == "dimension":
                dimensions.add(line)

    return metrics, dimensions

ALLOWED_METRICS, ALLOWED_DIMENSIONS = load_allowed_fields()

SYSTEM_PROMPT = f"""
You are a Google Analytics 4 query planner.

Task:
Convert a natural language question into a GA4 Data API query plan.

Rules (STRICT):
- Respond with ONLY valid JSON
- You may ONLY use metrics and dimensions from the allowed lists below
- Find the closest matching GA4 concept for each user concept
- If a concept cannot be mapped, OMIT it
- Do NOT include explanations
- Do NOT include markdown or code fences
- Output must be parseable by json.loads()

Allowed Metrics:
{', '.join(sorted(ALLOWED_METRICS))}

Allowed Dimensions:
{', '.join(sorted(ALLOWED_DIMENSIONS))}

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


class AnalyticsAgent:
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT

    def handle_query(self, query: str, property_id: str):
        llm_response = ask_llm(
            system_prompt=self.system_prompt,
            user_prompt=query
        )
        try:
            plan = self._extract_json(llm_response)
        except Exception as e:
            return {
                "error": "Failed to interpret analytics query.",
                "message": str(e)
            }

        invalid_metrics, invalid_dimensions = self._validate_plan(plan)

        if invalid_metrics or invalid_dimensions:
            return {
                "error": "Could not map query to valid GA4 fields.",
                "invalid_metrics": invalid_metrics,
                "invalid_dimensions": invalid_dimensions,
                "message": "Please rephrase your query using valid GA4 concepts."
            }
        if not plan.get("dimensions"):
            plan["dimensions"] = [{"name": "date"}]

        print("Executing GA4 query with plan:", plan)
        plan.setdefault("keepEmptyRows", True)
        response = run_ga4_query(plan, property_id)
        rows = response.get("rows", [])

        return {
            "query_plan": plan,
            "row_count": len(rows),
            "data": rows,
            "explanation": (
                "No data was found for this query."
                if not rows
                else "Here are the results based on your query."
            )
        }
    
    @staticmethod
    def _extract_json(text):
        if isinstance(text, dict):
            return text
        if not isinstance(text, str):
            raise TypeError(f"Expected str or dict, got {type(text)}")

        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("No JSON object found in LLM response")

        return json.loads(match.group())

    @staticmethod
    def _normalize_fields(items, field_name):
        normalized = []
        for item in items:
            if isinstance(item, str):
                normalized.append(item)
            elif isinstance(item, dict) and "name" in item:
                normalized.append(item["name"])
            else:
                raise ValueError(f"Invalid {field_name}: {item}")
        return normalized

    def _validate_plan(self, plan):
        metric_names = self._normalize_fields(plan.get("metrics", []), "metric")
        dimension_names = self._normalize_fields(plan.get("dimensions", []), "dimension")

        invalid_metrics = [m for m in metric_names if m not in ALLOWED_METRICS]
        invalid_dimensions = [d for d in dimension_names if d not in ALLOWED_DIMENSIONS]

        return invalid_metrics, invalid_dimensions
