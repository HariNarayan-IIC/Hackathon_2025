import os
import json
from dotenv import load_dotenv
from google import genai
import re

# Load API Key from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file.")

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

# Classifier Function
def classify_notification(title, content, source):
    prompt = f"""
You are a smart notification classifier.

Given the title, content, and source of a notification, return a JSON with:
- category: Work, Social, Finance, Promotions, System, Health, News, Entertainment
- priority: High, Medium, Low
- summary: a brief four-word summary of the notification's content

Respond ONLY in this JSON format:
{{
  "category": "<category>",
  "priority": "<priority>",
  "summary": "<summary>"
}}

Notification:
Title: {title}
Content: {content}
Source: {source}
"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",  # or "gemini-2.0-pro"
        contents=prompt
    )


    try:
        text = response.text
        # Step 1: Strip Markdown-style code block wrapper (```json ... ```)
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if not match:
            raise ValueError("No valid JSON code block found")

        json_str = match.group(1)

        # Step 2: Parse cleaned JSON string
        return json.loads(json_str)
    except Exception as e:
        print("⚠️ Could not parse JSON. Raw Gemini response:")
        print(response.text)
        return None

# Main Loop
# if __name__ == "__main__":
#     print("Classifier (type 'q' to quit)\n")

#     while True:
#         source = input("Enter source (or 'q' to quit): ").strip()
#         if source.lower() == 'q':
#             break

#         title = input("Title: ").strip()
#         content = input("Content: ").strip()

#         print("\nClassifying...")
#         result = classify_notification(title, content, source)

#         if result:
#             print("\nResult:")
#             print(json.dumps(result, indent=2))
#         print("\n" + "-"*40 + "\n")
