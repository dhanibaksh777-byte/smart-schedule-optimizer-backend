from dotenv import load_dotenv
import resend
import os


load_dotenv()

resend.api_key = os.getenv("resend_api_key")
if not resend.api_key:
    raise RuntimeError("resend api does'nt exists in .env file!")

def send_email(to_email : str,subject : str,html_content  : str):
    params = {
        "from" : "onboarding@resend.dev",
        "to" : [to_email],
        "subject" : subject,
        "html" :  html_content
    }


    try:
        response = resend.Emails.send(params)
        return response
    except Exception as e:
        print(f"email sending failed: {e}")
        return None









