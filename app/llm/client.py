from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("LITELLM_API_KEY"),
    base_url="http://3.110.18.218"
)

def ask_llm(system_prompt, user_prompt):
    print("Asking LLM...")
    print(f"System Prompt: {system_prompt}")
    print(f"User Prompt: {user_prompt}")
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )
    print("Received response from LLM.",response)
    return response.choices[0].message.content
