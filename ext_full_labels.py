import csv
import json
import os

def main():
    # Function to convert JSON bounding box data to 'x1, y1, x2, y2' format
    def convert_to_x1y1x2y2(json_data, image_name):
        csv_data = []
        for bbox in json_data:
            x1 = bbox['x']
            y1 = bbox['y']
            x2 = bbox['x'] + bbox['width']
            y2 = bbox['y'] + bbox['height']
            label = bbox.get("labels", "unknown")[0]
            box_id = bbox.get('id', 'unknown')
            csv_data.append([x1, y1, x2, y2, label, box_id, image_name])
        return csv_data

    # Input and output file paths
    input_file = 'input.csv'
    output_file = 'full_box_data.csv'

    # Read JSON data from input CSV file and write to output CSV file
    with open(input_file, 'r', encoding='ISO-8859-1') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.writer(outfile)
        
        # Write header
        writer.writerow(['x1', 'y1', 'x2', 'y2', 'labels', 'id', 'image_name'])
        
        for row in reader:
            # Extract image name from image URL
            image_url = row['image_url']
            image_name = os.path.basename(image_url).split('.')[0]

            # Convert JSON data to 'x1, y1, x2, y2' format
            json_data = json.loads(row['annotation_bboxes'])
            csv_data = convert_to_x1y1x2y2(json_data, image_name)
            
            # Write to output CSV file
            writer.writerows(csv_data)

if __name__ == "__main__":
    main()
