from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Metric, Dimension, RunReportRequest
)


def normalize_fields(items, field_name):
    """
    Ensures metrics/dimensions are plain strings.
    Accepts:
    - "activeUsers"
    - {"name": "activeUsers"}
    """
    normalized = []
    for item in items:
        if isinstance(item, str):
            normalized.append(item)
        elif isinstance(item, dict) and "name" in item:
            normalized.append(item["name"])
        else:
            raise ValueError(f"Invalid {field_name}: {item}")
    return normalized


def run_ga4_query(plan, property_id):
    client = BetaAnalyticsDataClient.from_service_account_file(
        "credentials.json"
    )
    print(f"Using property ID: {property_id}")
    metric_names = normalize_fields(plan["metrics"], "metric")
    dimension_names = normalize_fields(plan["dimensions"], "dimension")

    metrics = [Metric(name=m) for m in metric_names]
    dimensions = [Dimension(name=d) for d in dimension_names]

    date_ranges = []
    for dr in plan.get("dateRanges", []):
        start = dr.get("startDate", "14daysAgo")
        end = dr.get("endDate", "today")
        date_ranges.append(DateRange(start_date=start, end_date=end))
    
    if not date_ranges: 
        date_ranges = [DateRange(start_date="14daysAgo", end_date="today")]

    request = RunReportRequest(
        property=f"properties/{property_id}",
        metrics=metrics,
        dimensions=dimensions,
        date_ranges=date_ranges
    )
    response = client.run_report(request)
    rows = []
    for row in response.rows:
        rows.append({
            "dimensions": [d.value for d in row.dimension_values],
            "metrics": [m.value for m in row.metric_values]
        })

    return {"rows": rows}
