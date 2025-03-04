import requests
from dotenv import load_dotenv
import os


load_dotenv()
APPLICATION_INSIGHT_APP_ID = os.getenv("APPLICATION_INSIGHT_APP_ID")
APPLICATION_INSIGHT_API_KEY = os.getenv("APPLICATION_INSIGHT_API_KEY")


# Define your KQL query and timespan (e.g., last 1 day)
query = """
requests 
| where customDimensions['User.AuthenticatedUserId'] == "dagfinn.parnas@bouvet.no"
| project timestamp, name, url, resultCode, duration
"""
timespan = "P1D"  # ISO 8601 duration format for 1 day


# Construct the REST API URL
url = f"https://api.applicationinsights.io/v1/apps/{APPLICATION_INSIGHT_APP_ID}/query"

# Set the parameters and headers, including the API key
params = {
    "query": query,
    "timespan": timespan
}
headers = {
    "x-api-key": APPLICATION_INSIGHT_API_KEY
}

# Make the GET request
response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    data = response.json()
    print("Query Results:", data)
else:
    print("Error:", response.status_code, response.text)
