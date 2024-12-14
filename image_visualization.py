import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import json
import pandas as pd
import numpy as np


data1 = pd.read_csv('input.csv')
file_path = "nv_en_000146_0_ro_surya.json"  # Replace with your file's path

# Load the JSON file
with open(file_path, 'r') as file:
    data = json.load(file)

# Extract reading order
reading_order = [
    {
        "id": item["id"],
        "bbox": item["bbox"],
        "order": item["order"],
        "label": item["label"]
    }
    for item in data.get("reading_order", [])
]

# Extract and parse the ocr_surya_tl column
ocr_surya_tl_data = data1['ocr_surya_tl'].apply(json.loads)

# Convert the parsed data into a list of dictionaries with key `text_lines`
text_lines_data = ocr_surya_tl_data[0]

def draw_text_lines(image_size, text_lines_data):

    # Create a blank image

    # img = np.ones((image_size[0], image_size[1], 3), dtype=np.uint8) * 255  # White background



    # fig, ax = plt.subplots(figsize=(10, 10))

    # ax.imshow(img)
    # Loop through the data to extract bounding box and text info
    for entry in text_lines_data:
        if 'text_lines' in entry:
            for line in entry['text_lines']:

                bbox = line['bbox']  # Assuming bbox = [x_min, y_min, x_max, y_max]
                # width_im, height_im = image.size
                # x1 = bbox[0] * 0.3
                # y1 = bbox[1] * 2.35
                # x2 = bbox[2] * 0.3
                # y2 = bbox[3] * 2.35
    
                # Convert box coordinates to integers
                # bbox = (int(x1), int(y1), int(x2), int(y2))
        
                rect = plt.Rectangle(
                    (bbox[0], bbox[1]),  # Bottom-left corner
                    bbox[2] - bbox[0],  # Width
                    bbox[3] - bbox[1],  # Height
                    linewidth=1,
                    edgecolor='red',
                    facecolor='none'
                )
                ax.add_patch(rect)
                # # Add text inside the bounding box
                # ax.text(
                #     bbox[0], bbox[1] - 5, text, color='blue', fontsize=8, 
                #     verticalalignment='bottom', horizontalalignment='left'
                # )

    ax.axis('off')  # Hide axes
    plt.show()

image = Image.open("nv_en_000146_0.png")
fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(image)

draw_text_lines(image, text_lines_data)




# Image path (replace with the actual image file path)
image_path = "nv_en_000146_0.png"

# Load the image
image = Image.open(image_path)

# Create a Matplotlib figure
fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(image)

# Draw bounding boxes and annotate them
for item in reading_order:
    bbox = item['bbox']
    rect = patches.Rectangle(
        (bbox[0], bbox[1]),  # Bottom-left corner
        bbox[2] - bbox[0],  # Width
        bbox[3] - bbox[1],  # Height
        linewidth=2,
        edgecolor='red',
        facecolor='none'
    )
    ax.add_patch(rect)
    # Add text annotation (id, label, order)
    ax.text(
        bbox[0], bbox[1] + 70,  # Slightly above the bounding box
        f"{item['label']}\n{item['order']}", # f"{item['id']}\n{item['label']}\n{item['order']}"
        fontsize=6,
        color='blue',
        bbox=dict(facecolor='white', alpha=0.5, edgecolor='none')
    )

# Hide axes for better visualization
ax.axis('off')
plt.show()
file_path = "nv_en_000146_0_ro.json"  # Replace with your file's path

# Load the JSON file
with open(file_path, 'r') as file:
    data = json.load(file)

# Extract 'from_id' and 'to_id' pairs
relations = [
    {"from_id": relation["from_id"], "to_id": relation["to_id"]}
    for relation in data.get("bboxes_relation_json", [])
]


# Create a dictionary to quickly map IDs to bounding boxes
bbox_dict = {item['id']: item['bbox'] for item in reading_order}

# Load the image
image = Image.open("nv_en_000146_0.png")  # Replace with the correct image path

# Create the Matplotlib figure
fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(image)

# Draw the bounding boxes
for item in reading_order:
    bbox = item['bbox']
    rect = patches.Rectangle(
        (bbox[0], bbox[1]),
        bbox[2] - bbox[0],
        bbox[3] - bbox[1],
        linewidth=2,
        edgecolor='red',
        facecolor='none'
    )
    ax.add_patch(rect)
    # Annotate the box with ID and label
    ax.text(
        bbox[0], bbox[1] + 40,
        f"ID: {item['id']}\nLabel: {item['label']}",
        fontsize=8,
        color='blue',
        bbox=dict(facecolor='white', alpha=0.5, edgecolor='none')
    )

# Draw arrows based on from_id and to_id relationships
for relation in relations:
    from_id, to_id = relation['from_id'], relation['to_id']
    if from_id in bbox_dict and to_id in bbox_dict:
        # Calculate center points of the bounding boxes
        from_bbox = bbox_dict[from_id]
        to_bbox = bbox_dict[to_id]
        from_center = ((from_bbox[0] + from_bbox[2]) / 2, (from_bbox[1] + from_bbox[3]) / 2)
        to_center = ((to_bbox[0] + to_bbox[2]) / 2, (to_bbox[1] + to_bbox[3]) / 2)
        
        # Draw the arrow
        ax.annotate(
            '', xy=to_center, xytext=from_center,
            arrowprops=dict(arrowstyle="simple", color='black', lw=2, connectionstyle="arc3,rad=.5")
        )

# Hide axes for better visualization
ax.axis('off')
plt.show()
