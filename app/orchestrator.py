import os
from typing import Dict, Any

from dotenv import load_dotenv

from app.llm.client import ask_llm
from app.agents.seo_agent import SEOAgent
from app.agents.analytics_agent import AnalyticsAgent

load_dotenv()

SPREADSHEET_URL = os.getenv("SPREADSHEET_URL")

if not SPREADSHEET_URL:
    raise RuntimeError("SPREADSHEET_URL not set in environment")

INTENT_PROMPT = """
You are an intent classifier for a multi-agent analytics system.

Decide which agent(s) are required to answer the user's question.

Agents:
- seo: Uses llms to analyze SEO data from Google Sheets using Screaming Frog exports
- analytics: Uses Google Analytics 4 data
- both: Requires combining SEO + GA4 data

Rules:
- Respond with ONLY one of: seo, analytics, both
- No explanations
- No punctuation
- No markdown

Question:
{question}
"""

FINAL_ANSWER_PROMPT = """
You are an expert analytics assistant.

Using the agent outputs below, produce a clear, correct, and concise
natural-language answer for the user's question.

Rules:
- Do NOT mention agents, tools, or data sources
- Explain results in plain English
- If no data is found, clearly say so
- Be accurate and factual
- also answer like how an AI chatbot would do in a detailed and elaborate manner. (strictly follow this rule)
- There should be one proper answer to the user's question, like if the user asked for a particular metric value, then provide that value

SEO Result:
{seo_result}

Analytics Result:
{analytics_result}
"""


class Orchestrator:
    def __init__(self):
        self.seo_agent = SEOAgent(SPREADSHEET_URL)
        self.analytics_agent = AnalyticsAgent()

    def _detect_intent(self, question: str) -> str:
        response = ask_llm(
            system_prompt="You are a classifier.",
            user_prompt=INTENT_PROMPT.format(question=question)
        )
        return response.strip().lower()

    def handle_query(
        self,
        question: str,
        property_id: str | None = None
    ) -> Dict[str, Any]:
        """
        Main orchestration entrypoint
        """

        intent = self._detect_intent(question)
        print("Detected intent:", intent)

        seo_result = None
        analytics_result = None

        if intent in ("seo", "both"):
            seo_result = self.seo_agent.query(
                question=question,
                structured=True
            )

        if intent in ("analytics", "both"):
            if not property_id:
                return {
                    "error": "property_id is required for analytics queries"
                }

            analytics_result = self.analytics_agent.handle_query(
                query=question,
                property_id=property_id
            )

        final_answer = ask_llm(
            system_prompt="You generate final answers.",
            user_prompt=FINAL_ANSWER_PROMPT.format(
                seo_result=seo_result,
                analytics_result=analytics_result
            )
        )

        return {
            "intent": intent,
            "seo": seo_result,
            "analytics": analytics_result,
            "answer": final_answer.strip()
        }
