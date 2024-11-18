# Annotation Script for Shoonya

## Overview

This project provides an annotation script designed to simplify the annotators' tasks in Shoonya. The script processes an input CSV file with various details, including metadata about images and bounding boxes, to automate OCR and determine the reading order of text within the images. 

Shoonya does not directly accept string-based column data, so the script manages bounding box details separately and maps bounding boxes with their corresponding metadata into separate CSV files. 

By leveraging GPU batch processing, the script efficiently cuts images into bounding box shapes, performs OCR, and maps the results back to the original data structure.

---

## Input Details

The input file, `input.csv`, includes the following columns:
- `language`
- `image_url`
- `ocr_domain`
- `ocr_prediction_json`
- `task_status`
- `annotator_email`
- `ocr_transcribed_json`
- `bboxes_relation_json`
- `annotated_document_details_json`
- `id`
- `annotation_bboxes`
- `annotation_labels`
- `annotator`
- `annotation_id`
- `created_at`
- `updated_at`
- `lead_time`

---

## Functionality

1. **OCR Processing**:
   - Images listed in the `input.csv` are segmented into their respective bounding box shapes and save in a folder .
   - we extract bounding box details from annotation_bboxes column of input.csv , we also extract the detials of those bounding boxes with the bbox_id,label,language_code .
   - code inputs only bouding box details to surya-ocr as a output we recieve a the OCR data in yolo format they it gets converted to Shoonya format
   - the combined data of OCR of all bounding boxes of all the imges present in input,csv are saved in a json file.
   - as we have a intermediate tract of information of mapping of bounding boxes and labels,image_id we have to seperate them back to their origin image
   - These segments are processed using OCR in batches, optimized for GPU utilization.
   - The script tracks the origin of each bounding box, ensuring accurate mapping to the image and bounding box ID by creating an intermediate CSV files for bounding box details and their labels seperately.

2. **Batch Processing**:
   - Segmented bounding box images are processed together in batches for improved efficiency.
   - OCR results are aggregated for all bounding boxes in the batch.

3. **Output Separation**:
   - After processing, the OCR results are separated by their originating image IDs.
   - This ensures that the bounding box content is correctly associated with the relevant image.

4. **Reading Order**:
   - The script generates JSON files specifying the reading order of the bounding boxes.

5. **Update Input Data**:
   - The `input.csv` file is updated with the OCR-transcribed text for each bounding box and additional metadata.

---

## Workflow

1. **Input Preparation**:
   - Ensure the `input.csv` file is ready and contains all required columns.

2. **Run the Script**:
   - Execute the main script with the following command:
     ```bash
     python main.py -b 64
     ```
   - Replace `<batch_size>` with the number of images to process in a single batch.

3. **Output**:
   - The script updates the the "text": inside the annotation_bboxes column in  `input.csv` file for each bounding box.
   - Generates JSON files with image name for reading order.

---

## Key Features

- Efficient GPU-based batch OCR processing.
- Accurate tracking and mapping of bounding boxes and metadata.
- Automatic updates to the input file with OCR results and reading order details.
- Generation of reading order JSON files for further use.

---

## Notes

- Ensure all required dependencies are installed before running the script.
- Use batch processing for large datasets to maximize GPU efficiency.
- The script maintains a clear association between bounding boxes, their text, and metadata.

---

This script significantly reduces the effort required for annotators to process images, improving productivity and accuracy in Shoonya.
