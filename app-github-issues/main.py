import requests
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from context_manager import ContextManager

load_dotenv()

# Update use MCP approach
#context_manager = ContextManager()

llm = ChatOpenAI(model_name="gpt-4", temperature=0)

def get_issues():
    url = "https://api.github.com/repos/Bouvet-AI-Sandbox/mcp-bug-triage/issues"
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"
    }
    response = requests.get(url, headers=headers)
    
    # Check if the response is successful
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

def ask_openai_for_suggestions(issue_body):
    
    prompt = f"I encountered an issue with the following details:\n\n{issue_body}\n\nCan you suggest a solution?"
    response = llm.generate(
        prompt=prompt,
        max_tokens=150
    )
    return response.generations[0].text.strip()

if __name__ == "__main__":
    issues = get_issues()
    for issue in issues:
        print(f"Title: {issue['title']}")
        print(f"URL: {issue['html_url']}")
        print(f"Created by: {issue['user']['login']}")
        print(f"State: {issue['state']}")
        print(f"Body: {issue['body']}")
        print()
        
        # suggestion = ask_openai_for_suggestions(issue['body'])
        # print(f"OpenAI Suggestion: {suggestion}")
        # print()