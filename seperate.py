import csv
import json
import os

def read_csv(file_path):
    mapping = {}
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            box_id = row['id'].strip()  # strip whitespace if necessary
            image_name = row['image_name'].strip()  # strip whitespace if necessary
            if image_name not in mapping:
                mapping[image_name] = []
            mapping[image_name].append(box_id)
    return mapping

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def process_and_save_data(csv_mapping, combined_data):
    for image_name, ids in csv_mapping.items():
        image_data = [item for item in combined_data if item['id'] in ids]
        output_file = f"{image_name}_ocr.json"
        save_json(output_file, image_data)

    print("JSON files have been saved in the current directory.")

def main():
    # Define paths
    combined_json_path = 'combined_ocr_ocr.json'  # Path to the combined JSON file
    csv_file_path = 'full_box_data.csv'  # Path to the CSV file containing the box_id and image_name mapping

    with open(combined_json_path, 'r', encoding='utf-8') as f:
        combined_data = json.load(f)

    csv_mapping = read_csv(csv_file_path)
    print(csv_mapping)
    print(f"CSV mapping loaded with {len(csv_mapping)} image names")

    # Split the combined JSON file into separate JSON files by image name
    process_and_save_data(csv_mapping, combined_data)

if __name__ == "__main__":
    main()
