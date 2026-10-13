
import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = (
    "You are a friendly teaching assistant. "
    "Extract the 5 most important learning points "
    "and write a clear, conversational 5-minute recap podcast script."
    "Keep the script under 3,500 characters."
)

    
def create_script(transcript):
    if not transcript or not transcript.strip():
        raise ValueError("The transcript is empty.")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
    )

    return response.choices[0].message.content


