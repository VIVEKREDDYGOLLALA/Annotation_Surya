import csv
import json

def main():
    # Function to convert JSON bounding box data to 'x1, y1, x2, y2' format
    def convert_to_x1y1x2y2(json_data):
        csv_data = []
        for bbox in json_data:
            x1 = bbox['x']
            y1 = bbox['y']
            x2 = bbox['x'] + bbox['width']
            y2 = bbox['y'] + bbox['height']
            label = bbox.get("labels", "unknown")[0]
            box_id = bbox.get('id', 'unknown')
            csv_data.append([x1, y1, x2, y2, label, box_id])
        return csv_data

    # Input and output file paths
    input_file = 'input.csv'
    output_file = 'output2_1im.csv'

    # Read JSON data from input CSV file and write to output CSV file
    with open(input_file, 'r', encoding='ISO-8859-1') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.writer(outfile)
        
        # Write header
        writer.writerow(['x1', 'y1', 'x2', 'y2','labels','id'])
        
        for row in reader:
                # try:
                json_str = row.get('annotation_bboxes', '')
                # json_str = row.get('ocr_transcribed_json', '')
                if json_str.strip():
                    try:
                        json_data = json.loads(json_str)
                        # Convert JSON data to 'x1, y1, x2, y2' format
                        csv_data = convert_to_x1y1x2y2(json_data)
                        
                        # Write to output CSV file
                        writer.writerows(csv_data)
                    except json.JSONDecodeError:
                         print(f'Invalid JSON in row: {row}')
                else:
                    print(f'Empty JSON string in row: {row}')
                         

if __name__ == "__main__":
    main()
