from dotenv import load_dotenv
from groq import Groq
import os
from json import json,JSONDecodeError
from pydantic import ValidationError
from schemas import TaskAiExtraction

SYSTEM_PROMPT = """You are a precise task extraction assistant. 
Analyze the user's input text and extract the implied task details.

Rules:
1. Choose priority string: "high" (if urgent/important), "medium" (default), or "low".
2. Extract due_date as an ISO 8601 timestamp string (YYYY-MM-DDTHH:MM:SS) in UTC. 
3. If no specific date or time is mentioned by the user, you MUST set due_date to null.

Respond ONLY with the requested structured schema data."""


api_key = os.getenv("groq_api_key")
if not api_key:
    raise RuntimeError("groq api missing in .env file")
client = Groq(api_key=api_key)

def get_response(user_content : str):
    try:

        response1 = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role" : "user" , "content" : user_content},
                  {"role" : "assistant","content" : SYSTEM_PROMPT}
                  ],
                  response_format={"type" : "json_object"}      
        )
        raw_json_string = response1.choices[0].message
        parsed_data = json.loads(raw_json_string)
        validated_output = TaskAiExtraction(**parsed_data)
        return validated_output

    except JSONDecodeError:
        raise ValueError("Ai parsing Error:Response was not a valid strucutred output")
    except ValidationError as e:
        raise ValueError(f"AI validation error: Extracted keys do not align with requirements. Details: {e}")


    






   

