import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OWNER = "Bouvet-AI-Sandbox"
REPO = "mcp-bug-triage"

url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues"
headers = {"Authorization": f"token {GITHUB_TOKEN}"}
params = {"labels": "bug", "state": "all"}  # Get open and closed bugs

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    issues = response.json()
    for issue in issues:
        print(f"{issue['title']}: {issue['html_url']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
