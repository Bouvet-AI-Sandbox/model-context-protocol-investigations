import os
import requests
from dotenv import load_dotenv
from langchain.chains import LLMChain, SequentialChain


load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = "kjarisk"

def fetch_github_data():
    response = requests.get(
        f"https://api.github.com/users/{GITHUB_USERNAME}",
        headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
        },
        timeout=10,
    )
    return response

def process_github_response(response):
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Error: {response.status_code}"}

chain = LLMChain([fetch_github_data, process_github_response])

response = chain.run()

print(response)

