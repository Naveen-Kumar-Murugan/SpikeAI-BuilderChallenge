import pandas as pd
from app.services.sheets_service import build_union_table
from app.llm.client import ask_llm
from app.llm.prompts import seo_agent_prompt


class SEOAgent:
    def __init__(self, spreadsheet_url: str):
        self.spreadsheet_url = spreadsheet_url
        self.df = build_union_table(spreadsheet_url)

    def query(self, question: str, structured: bool = True):
        """
        Process an SEO question over the unified Screaming Frog dataset.
        """
        if self.df.empty:
            return {"error": "No data available from spreadsheet."}

        columns = self.df.columns.tolist()

        system_prompt = "You are a pandas code generator for SEO analysis."
        data_sample = self.df.head(20).to_dict(orient='records')
        user_prompt = seo_agent_prompt(columns, question, sample=data_sample)
        pandas_code = ask_llm(system_prompt, user_prompt)
        print("Generated pandas code:\n", pandas_code)

        try:
            local_vars = {"df": self.df.copy(), "pd": pd}
            exec(pandas_code, {}, local_vars)
            result_df = local_vars.get("result", pd.DataFrame())
        except Exception as e:
            return {"error": f"Failed to execute pandas code: {str(e)}"}

        if structured:
            return {
                "results": result_df.to_dict(orient="records"),
                "count": len(result_df),
            }
        else:
            return {
                "results": result_df.head(10).to_string(index=False),
                "count": len(result_df),
            }
