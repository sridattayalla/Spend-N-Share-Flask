# importing the requests library
import requests

# api-endpoint
URL = "http://127.0.0.1:5000/search"

# location given here
location = "delhi technological university"

# defining a params dict for the parameters to be sent to the API
PARAMS = [{'groupId': 5, 'key': '8688'}, {'groupId': 5, 'key': '86888'}, {'groupId': 5, 'key': '868887'}, {'groupId': 5, 'key': '8688871'}, {'groupId': 5, 'key': '86888712'} ]

# sending get request and saving the response as response object
r = requests.get(url=URL, params=PARAMS[0])

for i in range(5):
    requests.get(url=URL, params=PARAMS[1])

# extracting data in json format
data = r.json()

print(data)