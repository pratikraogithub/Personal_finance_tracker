import os
import requests
from dotenv import load_dotenv

# Load the .env file
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"

def query(prompt):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 150, "temperature": 0.7}
    }

    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    print("Status code:", response.status_code)
    print("Response text:", response.text)

    try:
        return response.json()
    except requests.JSONDecodeError:
        return {"error": "Response is not valid JSON", "text": response.text}

if __name__ == "__main__":
    prompt = "Explain the importance of budgeting in personal finance."
    result = query(prompt)

    # The response usually comes as a list with 'generated_text'
    if "error" not in result:
        try:
            print("AI Response:", result[0]["generated_text"])
        except (KeyError, IndexError):
            print("Unexpected response format:", result)
    else:
        print("AI Error:", result)
