import os
import pandas as pd
from urllib.request import urlopen
from PIL import Image, ImageDraw
import shutil

# Function to download image from URL
def download_image(url, save_path):
    with urlopen(url) as response:
        with open(save_path, 'wb') as out_file:
            out_file.write(response.read())

# Function to crop and save image with bounding box overlay
def crop_and_save_image(image_path, box, save_folder, box_id):
    img = Image.open(image_path)
    
    # Calculate pixel coordinates from percentage
    width_im, height_im = img.size
    x1 = box[0] * width_im / 100
    y1 = box[1] * height_im / 100
    x2 = box[2] * width_im / 100
    y2 = box[3] * height_im / 100
    
    # Convert box coordinates to integers
    box = (int(x1), int(y1), int(x2), int(y2))
    
    # Check if label is in the list of labels to skip cropping
    if box_id.split('_')[0] in ['figure', 'footer', 'header']:
    
        return
    
    # Crop image
    cropped_img = img.crop(box)
    
    # Save the cropped image with bounding box overlay
    save_path = os.path.join(save_folder, f"{box_id}.png")
    
    # Resize the cropped image
    new_height = 400
    aspect_ratio = cropped_img.width / cropped_img.height
    new_width = int(new_height * aspect_ratio)
    resized_img = cropped_img.resize((new_width, new_height), Image.LANCZOS)
    
    resized_img.save(save_path)


# Main function to orchestrate the entire process
def main(start, batch_size):
    # Paths to input CSV files
    input_csv_path = 'input.csv'
    full_box_data_csv_path = 'full_box_data.csv'

    # Read input data from CSV files
    input_data = pd.read_csv(input_csv_path)
    full_box_data = pd.read_csv(full_box_data_csv_path)

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
        # print(type(image_url))
        image_name = image_url.split('/')[-1]
        # print(type(image_name))
        image_name = image_name.split('.')[0]
        # print(image_name)

        # Download image to temporary folder
        image_path_temp = os.path.join(temp_folder, f"{image_name}.jpg")
        download_image(image_url, image_path_temp)

        # Find all boxes corresponding to this image_name in full_box_data
        relevant_boxes = full_box_data[full_box_data['image_name'] == image_name]

        # Iterate through each relevant box for this image
        for _, box_row in relevant_boxes.iterrows():
            bbox = [
                box_row['x1'], 
                box_row['y1'], 
                box_row['x2'], 
                box_row['y2']
            ]
            
            box_id = box_row['id']
            labels = box_row['labels']

            # Check if label is in the list of labels to skip cropping
            if labels in ['figure', 'footer', 'header']:
                continue

            # Crop and save the image with bounding box overlay
            crop_and_save_image(image_path_temp, bbox, save_folder, box_id)

        # Delete original image after processing all boxes for this image
        os.remove(image_path_temp)

    # Clean up temporary folder after all images have been processed
    shutil.rmtree(temp_folder)

if __name__ == "__main__":
    main(start, batch_size)
