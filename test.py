input_file_path = 'results/surya/results/results.json'
import json

with open(input_file_path, "r") as file:
    data = json.load(file)

print(data.head())