import csv
import shutil
import os
import ext_boxes
import ext_labels
import reading_order
import ext_full_labels
import cut_save
import ocr
import seperate


def run_ocr(start, batch_size):
    cut_save.main(start, batch_size)
    ext_full_labels.main()
    ocr.main()
    seperate.main()


def run_ro(image_url):
    # Execute the functionalities from the three scripts
    ext_boxes.main(image_url)
    ext_labels.main()
    reading_order.main(image_url)
    
    results_folder = 'results'
    if os.path.exists(results_folder) and os.path.isdir(results_folder):
        shutil.rmtree(results_folder)
        print(f"Deleted folder: {results_folder}")
    
    image_name = image_url.split('/')[-1].split('.')[0]
    for file_name in [f"{image_name}_relations.json",f"{image_name}_ro.json"]:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Deleted file: {file_name}")

def main():
    input_file = 'input.csv'  
    # Read the image URLs from the CSV file
    with open(input_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            image_url = row['image_url']
            print
            run_ro(image_url)
    run_ocr()
    
if __name__ == "__main__":
    main()
