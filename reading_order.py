import requests
from PIL import Image
import csv
import json
import os
import pandas as pd
from surya.ordering import batch_ordering
from surya.model.ordering.processor import load_processor
from surya.model.ordering.model import load_model

HEADER_FOOTER_LABELS = {'header', 'footer'}

def download_image(image_url, save_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        raise Exception(f"Failed to download image from {image_url}")

def read_csv(file_path):
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        data = [list(map(float, row[:4])) for row in reader]  # Only read the first 4 columns as floats
    return data

def read_labels_csv(file_path):
    labels_with_ids = []
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  # Skip the header row
        labels_with_ids.append(header)
        for row in reader:
            labels_with_ids.append(row)
    return labels_with_ids

def convert_to_tuples(order_predictions, width_im, height_im, labels_with_ids):
    tuples = []
    header_footer_ids = {}
    label_index = 1  # Start from 1 to skip the header row
    
    for order_result in order_predictions:
        boxes = []
        for order_box in order_result.bboxes:
            bbox = order_box.bbox
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            label_row = labels_with_ids[label_index]
            label, box_id = label_row[4], label_row[5]
            label_index += 1
            
            if label in HEADER_FOOTER_LABELS:
                if label not in header_footer_ids:
                    header_footer_ids[label] = box_id
                box_id = header_footer_ids[label]
                
            boxes.append({
                'id': box_id,
                'bbox': [(bbox[0] * width_im) / 100, (bbox[1] * height_im) / 100,
                         (bbox[2] * width_im) / 100, (bbox[3] * height_im) / 100],
                'order': order_box.position,
                'label': label
            })
        tuples.append(boxes)
    return tuples

def generate_relations_json(order_predictions_tuples):
    relations = []
    headers_footers = []

    for boxes in order_predictions_tuples:
        for box in boxes:
            if box['label'] in HEADER_FOOTER_LABELS:
                headers_footers.append(box)

    def is_inside_header_footer(box):
        x1, y1, x2, y2 = box['bbox']
        for hf in headers_footers:
            hf_x1, hf_y1, hf_x2, hf_y2 = hf['bbox']
            if x1 >= hf_x1 and y1 >= hf_y1 and x2 <= hf_x2 and y2 <= hf_y2:
                return True
        return False

    for boxes in order_predictions_tuples:
        for i in range(len(boxes) - 1):
            if not is_inside_header_footer(boxes[i]) and not is_inside_header_footer(boxes[i + 1]):
                relations.append({
                    "type": "relation",
                    "to_id": boxes[i + 1]['id'],
                    "labels": ["continues-to"],
                    "from_id": boxes[i]['id'],
                    "direction": "right"
                })
    return {"bboxes_relation_json": relations}

def generate_reading_order_json(order_predictions_tuples):
    reading_order = []
    for boxes in order_predictions_tuples:
        for box in boxes:
            reading_order.append({
                "id": box['id'],
                "bbox": box['bbox'],
                "order": box['order'],
                "label": box['label']
            })
    return {"reading_order": reading_order}

# def update_csv_with_json(RELATIONS_JSON_PATH, input_csv_file):
#     # Check if the CSV file exists
#     if os.path.exists(input_csv_file):
#         df = pd.read_csv(input_csv_file)
#     else:
#         df = pd.DataFrame(columns=['reading_order_json'])

#     # Read the JSON data from the file
#     with open(RELATIONS_JSON_PATH, 'r', encoding='utf-8') as ro_file:
#         reading_order_json = ro_file.read()
    
#     # Update the first row or add a new row if the CSV is empty
#     if not df.empty:
#         df.loc[i, 'reading_order_json'] = reading_order_json
#         i+=1
#     else:
#         df = pd.DataFrame([{'reading_order_json': reading_order_json}])
    
#     # Save the updated DataFrame to the CSV file
#     df.to_csv(input_csv_file, index=False)
#     print(f"CSV file '{input_csv_file}' updated with reading order JSON data from '{RELATIONS_JSON_PATH}'.")

def main(image_url):
    image_name = image_url.split('/')[-1].split('.')[0]
    CSV_FILE_PATH = 'output_boxes_1_im.csv'
    LABELS_CSV_FILE_PATH = 'output2_1im.csv'
    LOCAL_IMAGE_PATH = 'downloaded_image.png'
    OUTPUT_CSV_PATH = 'input.csv'
    RELATIONS_JSON_PATH = f"{image_name}_ro.json"
    READING_ORDER_JSON_PATH = f"{image_name}_ro_surya.json"

    download_image(image_url, LOCAL_IMAGE_PATH)

    image = Image.open(LOCAL_IMAGE_PATH)
    width_im, height_im = image.size

    bboxes = read_csv(CSV_FILE_PATH)

    model = load_model()
    processor = load_processor()

    order_predictions = batch_ordering([image], [bboxes], model, processor)

    labels_with_ids = read_labels_csv(LABELS_CSV_FILE_PATH)

    order_predictions_tuples = convert_to_tuples(order_predictions, width_im, height_im, labels_with_ids)

    relations_json = generate_relations_json(order_predictions_tuples)
    with open(RELATIONS_JSON_PATH, 'w', encoding='utf-8') as json_file:
        json.dump(relations_json, json_file, indent=2)

    reading_order_json = generate_reading_order_json(order_predictions_tuples)
    with open(READING_ORDER_JSON_PATH, 'w', encoding='utf-8') as json_file:
        json.dump(reading_order_json, json_file, indent=2)
    row_index=0
    # update_csv_with_json(RELATIONS_JSON_PATH, OUTPUT_CSV_PATH, row_index)
    # print(f"Relations JSON saved to {RELATIONS_JSON_PATH}")

if __name__ == "__main__":
    image_url = input("Enter the image URL: ")
    main(image_url)
