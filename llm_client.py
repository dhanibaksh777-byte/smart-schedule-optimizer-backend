from dotenv import load_dotenv
from groq import Groq
import os
from json import JSONDecodeError
import json
from pydantic import ValidationError
from schemas import TaskAiExtraction


SYSTEM_PROMPT = """You are a precise task extraction assistant. 
Analyze the user's input text and extract the implied task details.

Rules:
1. Choose priority string: "high" (if urgent/important), "medium" (default), or "low".
2. Extract due_date as an ISO 8601 timestamp string (YYYY-MM-DDTHH:MM:SS) in UTC. 
3. If no specific date or time is mentioned by the user, you MUST set due_date to null.

Respond ONLY with a valid JSON object matching the requested schema."""


api_key = os.getenv("groq_api_key")
if not api_key:
    raise RuntimeError("groq api missing in .env file")
client = Groq(api_key=api_key)

from datetime import datetime, timezone

def get_response(user_content: str):
    current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    system_prompt_with_date = SYSTEM_PROMPT + f"\n\nToday's date is {current_date}. Calculate all relative dates (like 'next Friday', 'tomorrow', 'in 3 days') based on this actual current date."
    
    try:
        response1 = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt_with_date},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"}
        )
        raw_json_string = response1.choices[0].message.content
        parsed_data = json.loads(raw_json_string)
        validated_output = TaskAiExtraction(**parsed_data)
        return validated_output

    except JSONDecodeError:
        raise ValueError("AI parsing error: Response was not valid structured output")
    except ValidationError as e:
        raise ValueError(f"AI validation error: Extracted keys do not align with requirements. Details: {e}")
    except Exception as e:
        raise ValueError(f"AI service error: {str(e)}")