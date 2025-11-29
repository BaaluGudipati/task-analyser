import requests
import json

# Test data
tasks = [
    {
        "id": 1,
        "title": "OVERDUE: Fix critical bug",
        "due_date": "2025-11-25",
        "estimated_hours": 2,
        "importance": 9,
        "dependencies": []
    },
    {
        "id": 2,
        "title": "Quick: Update README",
        "due_date": "2025-12-10",
        "estimated_hours": 1,
        "importance": 5,
        "dependencies": []
    }
]

# Send request
url = "http://127.0.0.1:8000/api/tasks/analyze/"
payload = {
    "tasks": tasks,
    "strategy": "smart_balance"
}

response = requests.post(url, json=payload)

# Print results
print("Status Code:", response.status_code)
print("\nResponse:")
print(json.dumps(response.json(), indent=2))