import os
import csv
import json
from urllib.request import urlopen
from PIL import Image
import shutil
import pandas as pd

# Function to download image from URL
def download_image(url, save_path):
    with urlopen(url) as response:
        with open(save_path, 'wb') as out_file:
            out_file.write(response.read())

# Function to load CSV data
def load_csv(file_path):
    data = {}
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            bbox_id = row['id']  # Map bbox_id directly
            x1, y1, x2, y2 = map(float, [row['x1'], row['y1'], row['x2'], row['y2']])
            data[bbox_id] = {
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2
            }
    return data

# Function to adjust text line bounding boxes
def convert_text_lines_to_image_coordinates(results, csv_data):
    updated_results = {}

    for image_id, text_data_list in results.items():
        updated_text_lines = []

        # Loop through each text_data object
        for text_data in text_data_list:
            for text_line in text_data['text_lines']:
                # Find matching CSV data using the bbox ID
                bbox_id = image_id
                if bbox_id not in csv_data:
                    continue

                bbox_details = csv_data[bbox_id]
                bbox_x1, bbox_y1, bbox_x2, bbox_y2 = bbox_details['x1'], bbox_details['y1'], bbox_details['x2'], bbox_details['y2']
                bbox_width = bbox_x2
                bbox_height = bbox_y2

                # Adjust text line coordinates relative to the bounding box
                line_bbox = text_line['bbox']
                adjusted_bbox = [
                    bbox_x1 + (line_bbox[0] / 100) * bbox_width,
                    bbox_y1 + (line_bbox[1] / 100) * bbox_height,
                    bbox_x1 + (line_bbox[2] / 100) * bbox_width,
                    bbox_y1 + (line_bbox[3] / 100) * bbox_height
                ]

                # Update text line with the new bounding box
                updated_line = text_line.copy()
                updated_line['bbox'] = [round(coord) for coord in adjusted_bbox]
                updated_text_lines.append(updated_line)

        updated_results[image_id] = {'text_lines': updated_text_lines}

    return updated_results

# Function to crop and save images based on bounding boxes
def crop_and_save_image(image_path, box, save_folder, box_id):
    img = Image.open(image_path)

    # Convert box coordinates to integers
    box = (int(box[0]), int(box[1]), int(box[2]), int(box[3]))

    # Crop image
    cropped_img = img.crop(box)

    # Save the cropped image
    save_path = os.path.join(save_folder, f"{box_id}.png")

    # Resize the cropped image
    new_height = cropped_img.height
    aspect_ratio = cropped_img.width / cropped_img.height
    new_width = cropped_img.width
    resized_img = cropped_img.resize((new_width, new_height), Image.LANCZOS)

    resized_img.save(save_path)

# Main script
def main(start, batch_size):
    csv_file = 'full_box_data.csv'
    json_file = r'results\surya\results\results.json'
    input_csv_path = 'input.csv'
    output_file = r'results\surya\results\results.json'

    # Load data
    csv_data = load_csv(csv_file)

    with open(json_file, 'r') as file:
        results_data = json.load(file)

    # Convert coordinates
    updated_results = convert_text_lines_to_image_coordinates(results_data, csv_data)

    # Save updated results
    with open(output_file, 'w') as file:
        json.dump(updated_results, file, indent=4)

    print(f"Updated results saved to {output_file}")

    # Read input data from CSV
    input_data = pd.read_csv(input_csv_path)

    # Create folder to save cropped images
    save_folder = os.path.join('results')
    os.makedirs(save_folder, exist_ok=True)

    # Temporary folder to download images
    temp_folder = 'temp_images'
    os.makedirs(temp_folder, exist_ok=True)

    # Iterate through each row in input_data
    input_data = input_data[start:start + batch_size]
    for index, row in input_data.iterrows():
        image_url = row['image_url']
        image_id = row['id']  # Match using the 'id' field

        # Download image to temporary folder
        image_path_temp = os.path.join(temp_folder, f"{image_id}.jpg")
        download_image(image_url, image_path_temp)

        # Find all boxes corresponding to this image_id in csv_data
        if image_id in csv_data:
            bbox = [
                csv_data[image_id]['x1'],
                csv_data[image_id]['y1'],
                csv_data[image_id]['x2'],
                csv_data[image_id]['y2']
            ]

            # Crop and save the image with bounding box overlay
            crop_and_save_image(image_path_temp, bbox, save_folder, image_id)

        # Delete original image after processing all boxes for this image
        os.remove(image_path_temp)

    # Clean up temporary folder after all images have been processed
    shutil.rmtree(temp_folder)

if __name__ == '__main__':
    start = 0  # Starting index for processing
    batch_size = 10  # Number of rows to process per batch
    main(start, batch_size)
