from app.agents.analytics_agent import handle_analytics_query

def handle_query(req):
    query = req.query.lower()

    # Very simple intent detection (for now)
    is_analytics = any(
        word in query for word in [
            "page", "views", "users", "sessions", "traffic"
        ]
    )
    # if is_analytics:
    if not req.propertyId:
        raise ValueError("propertyId is required for GA4 queries")
    return handle_analytics_query(req.query, req.propertyId)

    # return {
    #     "error": "Unsupported query type for now"
    # }
