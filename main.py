import csv
import shutil
import os
import argparse
from glob import glob
import ext_boxes
import ext_labels
import reading_order
import ext_full_labels
import cut_save
import ocr
import seperate


def run_ocr(start, batch_size):
    """
    Executes OCR-related tasks in a batch.
    """
    cut_save.main(start, batch_size)
    ext_full_labels.main()
    ocr.main()
    seperate.main()


def run_ro(image_urls):
    """
    Executes region order-related tasks for a list of images.
    """
    for image_url in image_urls:
        # Execute the functionalities from the three scripts
        ext_boxes.main(image_url)
        ext_labels.main()
        reading_order.main(image_url)

        # Remove the results folder if it exists
        results_folder = 'results'
        if os.path.exists(results_folder) and os.path.isdir(results_folder):
            shutil.rmtree(results_folder)
            print(f"Deleted folder: {results_folder}")

        # Remove generated reading order JSON file
        image_name = image_url.split('/')[-1].split('.')[0]
        for file_name in [f"{image_name}_ro_surya.json"]:
            if os.path.exists(file_name):
                os.remove(file_name)
                print(f"Deleted file: {file_name}")


def main(batch_size):
    """
    Main function to process images in batches.
    """
    input_file = 'input.csv'

    # Read the image URLs from the CSV file
    with open(input_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        image_urls = [row['image_url'] for row in reader]

    # Process images in batches
    total_images = len(image_urls)
    for i in range(0, total_images, batch_size):
        batch = image_urls[i:i + batch_size]
        print(f"Processing batch {i // batch_size + 1} of size {len(batch)}:")
        run_ro(batch)
        run_ocr(i, batch_size)

        # Clean up results folder after processing
        results_folder = 'results'
        if os.path.exists(results_folder):
            shutil.rmtree(results_folder)
            print(f"Deleted folder: {results_folder}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process images in batches with OCR.')
    parser.add_argument('-b', '--batch_size', type=int, default=5,
                        help='Number of images to process in each batch')
    args = parser.parse_args()

    main(args.batch_size)
