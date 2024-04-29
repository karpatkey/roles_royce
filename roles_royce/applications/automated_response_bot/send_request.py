import json
import requests
import os

def send_webhook(filename):

        # Get the current directory
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # Construct the full path to the JSON file
    filepath = os.path.join(current_dir, filename)
    # Open the JSON file and load its content
    with open(filepath, 'r') as file:
        data = json.load(file)

    # Send the JSON data as a POST request
    response = requests.post('http://localhost:8000/webhook', json=data)

    # Print the response
    print("Response:", response.status_code)
    print(response.json())

send_webhook('webhook.json')