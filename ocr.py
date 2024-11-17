import json
import csv
import subprocess
import os
import pandas as pd

current_row = 0

def get_languages_from_csv(input_csv_file):
    global current_row

    languages = []
    try:
        # Open the CSV file with UTF-8 encoding
        with open(input_csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                if i == current_row:
                    if 'language' in row:
                        language_str = row['language']
                        if language_str:
                            languages.extend(language_str.split(','))
                            languages = [lang.strip() for lang in languages if lang.strip()]
                            current_row += 1
                            return languages
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}. Attempting to read the file with 'latin-1' encoding.")
        # Fallback to latin-1 encoding if UTF-8 fails
        with open(input_csv_file, 'r', encoding='latin-1') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                if i == current_row:
                    if 'language' in row:
                        language_str = row['language']
                        if language_str:
                            languages.extend(language_str.split(','))
                            languages = [lang.strip() for lang in languages if lang.strip()]
                            current_row += 1
                            return languages
    return None

def read_lang_codes(lang_code_file):
    lang_codes = {}
    with open(lang_code_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            lang_codes[row[0]] = row[1]
    return lang_codes

def crop_and_run_ocr(input_csv_file='input.csv', lang_code_file='lang_code.csv'):
    languages = get_languages_from_csv(input_csv_file)
    if languages:
        lang_str = languages[0]
        lang_str = lang_str.strip("'[]'")
        languages = lang_str.split(',')
    print("Languages:", languages)

    lang_codes = read_lang_codes(lang_code_file)
    print("Language Codes:", lang_codes)
    
    lang_args = ','.join([lang_codes.get(lang, lang) for lang in languages] + ['en'])
    print("Language Arguments:", lang_args)
    return lang_args

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"The command '{command}' failed with return code {e.returncode}")

def combine_text(data, csv_file):
    combined_data = []

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_data = list(reader)

    csv_lookup = {entry['id']: {
        'x': float(entry['x1']),
        'y': float(entry['y1']),
        'width': float(entry['x2']) - float(entry['x1']),
        'height': float(entry['y2']) - float(entry['y1']),
        'labels': [entry['labels']],
        'id': entry['id']
    } for entry in csv_data}

    print("CSV Lookup:", csv_lookup)
    print("Data Structure:", json.dumps(data, indent=2))

    for id_key, id_data in data.items():
        print(f"Processing ID: {id_key}")
        print(f"ID Data: {id_data}")
        
        combined_text = []
        if isinstance(id_data, list):
            for item in id_data:
                if 'text_lines' in item:
                    for text_line in item['text_lines']:
                        combined_text.append(text_line['text'])

            if id_key in csv_lookup:
                is_figure = 'figure' in csv_lookup[id_key]['labels']

                combined_entry = {
                    'text': "" if is_figure else " ".join(combined_text),
                    **csv_lookup[id_key]
                }
                combined_data.append(combined_entry)
            else:
                print(f"Warning: ID '{id_key}' from JSON data not found in CSV file.")
        else:
            print(f"Error: Expected list for id_data, but got {type(id_data).__name__}")

    for entry in csv_data:
        if entry['labels'] == 'figure' and entry['id'] not in data:
            combined_entry = {
                'text': "",
                'x': float(entry['x1']),
                'y': float(entry['y1']),
                'width': float(entry['x2']) - float(entry['x1']),
                'height': float(entry['y2']) - float(entry['y1']),
                'rotation': 0,
                'labels': [entry['labels']],
                'id': entry['id'],
                'parentID': ""
            }
            combined_data.append(combined_entry)

    return combined_data

def run(input_file, csv_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    combined_data = combine_text(data, csv_file)

    formatted_data = [
        {
            "x": entry['x'],
            "y": entry['y'],
            "width": entry['width'],
            "height": entry['height'],
            "rotation": 0,
            "labels": entry['labels'],
            "text": entry['text'],
            "id": entry['id'],
            "parentID": ""
        }
        for entry in combined_data
    ]

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, ensure_ascii=False, indent=4)
    print(f"Combined data saved to {output_file}")

def update_csv_with_json(input_csv_file):
    # Check if the CSV file exists
    if os.path.exists(input_csv_file):
        df = pd.read_csv(input_csv_file)
    else:
        print(f"Error: CSV file '{input_csv_file}' not found.")
        return
    
    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # Extract image_name from image_url column
        image_url = row['image_url']
        image_name = image_url.split('/')[-1].split('.')[0]  # Extract image name from URL
        
        # Construct path to JSON file based on image_name
        json_file_path = f"{image_name}_ocr.json"
        
        # Check if JSON file exists
        if os.path.exists(json_file_path):
            # Read the JSON data from the file
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                json_data = json.load(json_file)
            
            # Update the row in the DataFrame with JSON data
            for key, value in json_data.items():
                df.at[index, key] = value  # Add each key-value pair from JSON to DataFrame
    
    # Save the updated DataFrame to the CSV file
    df.to_csv(input_csv_file, index=False)
    print(f"CSV file '{input_csv_file}' updated with JSON data.")

def main():
    input_file_path = 'results/surya/results/results.json'
    image_name = 'combined_ocr'
    csv_file = 'full_box_data.csv'
    output_file = f"{image_name}_ocr.json"
    input_csv_file= 'input.csv'

    lang_code_file = 'lang_code.csv'
    input_csv_file = 'input.csv'
    
    lang_args = crop_and_run_ocr(input_csv_file, lang_code_file)
    folder_path = 'results'
    command_to_run = f'surya_ocr {folder_path} --images --langs {lang_args}'
    run_command(command_to_run)
    run(input_file_path, csv_file, output_file)
    update_csv_with_json(input_csv_file)

if __name__ == "__main__":
    main()
