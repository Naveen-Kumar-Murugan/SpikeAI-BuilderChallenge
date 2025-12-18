def seo_agent_prompt(columns: list, question: str, sample: list = None) -> str:
    cols_str = ", ".join(columns)
    sample_str = f"Sample data:\n{sample}" if sample else ""
    
    return f"""
You are an SEO data analyst.

You are given a pandas DataFrame named `df` with the following columns:
{cols_str}

{sample_str}

Rules (STRICT):
- Use ONLY the columns listed above.
- Do NOT invent or rename columns.
- If a column represents dates, detect the format from the data and parse safely using dateutil.parser.
- Assign the final output to a variable named `result`.
- The result must always be a DataFrame, even if selecting a single column.
- Use pandas only.
- No comments, no explanations, no markdown.

Task:
Convert the following user question into pandas code that operates on `df`.
Question:
{question}
"""
