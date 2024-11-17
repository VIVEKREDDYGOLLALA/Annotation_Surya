import csv
import json
import os

def compress_json_file(json_file):
    """Reads a JSON file and returns its contents as a compressed single-line JSON string."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return json.dumps(data, separators=(',', ':'), ensure_ascii=False)

def add_json_columns_to_csv(input_csv, output_csv):
    """Adds 'ro_json' and 'ocr_json' columns to the CSV file based on image_url."""
    # Initialize CSV reader and writer
    with open(input_csv, 'r', encoding='utf-8') as infile, open(output_csv, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['ro_json', 'ocr_json']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Process each row in the CSV
        for row in reader:
            image_url = row['image_url']
            image_name = image_url.split('/')[-1].split('.')[0]
            
            ro_json_file = f'{image_name}_ro.json'
            ocr_json_file = f'{image_name}_ocr.json'
            
            if os.path.exists(ro_json_file):
                ro_json_compressed = compress_json_file(ro_json_file)
            else:
                ro_json_compressed = ''
            
            if os.path.exists(ocr_json_file):
                ocr_json_compressed = compress_json_file(ocr_json_file)
            else:
                ocr_json_compressed = ''
            
            # Update the row with compressed JSON contents
            row['ro_json'] = ro_json_compressed
            row['ocr_json'] = ocr_json_compressed
            
            # Write the updated row to the output CSV file
            writer.writerow(row)

if __name__ == "__main__":
    input_csv = 'input.csv'   # Replace with your input CSV file path
    output_csv = 'output.csv' # Replace with your output CSV file path
    
    add_json_columns_to_csv(input_csv, output_csv)
    print(f'CSV file with added columns "ro_json" and "ocr_json" created: {output_csv}')
