import requests
import json

url = 'https://openneuro.org/crn/graphql'
query = """
{
  dataset(id: "ds003029") {
    draft {
      summary {
        size
      }
    }
  }
}
"""
response = requests.post(url, json={'query': query})
data = response.json()
print(json.dumps(data, indent=2))
