import os
import re
import json
from dotenv import load_dotenv
from google import genai
# from google.genai.errors import ServerError

# Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found.")

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

# Enhanced Prompt Generator
def generate_prompt(category, priority, avg_reaction_time, click_count, dismiss_count, creation_datetime):
    prompt = f"""
You are an intelligent assistant that recommends optimized scheduling for mobile notifications to maximize user engagement and minimize fatigue.

## Notification Metadata:
- Created At: {creation_datetime}
- Category: {category}
- Priority: {priority}
- Average Reaction Time: {avg_reaction_time if avg_reaction_time is not None else "not available"} seconds
- Click Count: {click_count if click_count is not None else "not available"}
- Dismiss Count: {dismiss_count if dismiss_count is not None else "not available"}

## Behavior Analysis Guidelines:
- Lower average reaction time (under 30 seconds) = user is highly responsive. Increase frequency.
- High click count and low dismiss count = user finds notifications valuable. Increase frequency.
- High dismiss count or low click count = user is ignoring or annoyed. Reduce frequency.
- If no user data is available, be conservative in frequency (1-2 notifications).

## Category Behavior Hints:
- *Work / Finance / System*: Send early (morning/daytime). High priority means high urgency.
- *Social / News / Entertainment*: Send in the evening or break times. Low/medium priority = casual.
- *Health*: Time-sensitive, especially for reminders.
- *Promotions*: Low priority unless user engages often (high clicks/low dismisses).

## Priority Rules:
- *High Priority*: Must be seen quickly. Use shorter intervals and earlier start times.
- *Medium Priority*: Balanced exposure during active hours.
- *Low Priority*: Send during non-critical hours, with minimal frequency.

## Instructions:
1. Base all times on the provided creation datetime ({creation_datetime}).
2. Ensure startdatetime is same day or later, and enddatetime is after that.
3. Respond strictly in this JSON format:
{{
  "startdatetime": "YYYY-MM-DD HH:MM",
  "enddatetime": "YYYY-MM-DD HH:MM",
  "frequency": integer
}}
"""
    return prompt

# scheduler function
def get_schedule(prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    text = response.text
    # Step 1: Strip Markdown-style code block wrapper (```json ... ```)
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not match:
        raise ValueError("No valid JSON code block found")

    json_str = match.group(1)

    # Step 2: Parse cleaned JSON string
    return json.loads(json_str)


# Input Form
def get_user_input():
    print("\nEnter Notification Info (type 'e' to stop):")

    category = input("Notification category (required): ").strip()
    if category.lower() == "e":
        return None

    while not category:
        category = input("Category is required. Please enter again: ").strip()

    priority = input("Notification priority (required): ").strip()
    while not priority:
        priority = input("Priority is required. Please enter again: ").strip()

    try:
        avg_reaction_time = input("Avg. reaction time in seconds (optional): ").strip()
        avg_reaction_time = int(avg_reaction_time) if avg_reaction_time else None

        click_count = input("Click count (optional): ").strip()
        click_count = int(click_count) if click_count else None

        dismiss_count = input("Dismiss count (optional): ").strip()
        dismiss_count = int(dismiss_count) if dismiss_count else None
    except ValueError:
        print("Invalid input. Optional fields will be ignored.")
        avg_reaction_time = click_count = dismiss_count = None

    return category, priority, avg_reaction_time, click_count, dismiss_count

# Main loop
# if __name__ == "__main__":
#     while True:
#         user_data = get_user_input()
#         if user_data is None:
#             print("Exiting scheduler.")
#             break

#         cat, pri, art, cc, dc = user_data
#         prompt = generate_prompt(cat, pri, art, cc, dc)
#         result = get_schedule(prompt)

#         print("\nSuggested Notification Schedule:")
#         print(result)
