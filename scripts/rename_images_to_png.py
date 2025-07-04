from glob import glob
from PIL import Image
import os

# List of category folders and their filename patterns
categories = [
    ('cab', 'cab-'),
    ('bus', 'bus-'),
    ('train', 'train-'),
    ('hotels', 'hotel-'),
    ('air', 'air-'),
    ('alsp', 'alsp-'),  # Added support for alsp category
]

base_dir = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'images')

def convert_and_rename(folder, prefix):
    folder_path = os.path.join(base_dir, folder)
    for jpg_file in glob(os.path.join(folder_path, f'{prefix}*.jpg')):
        # Remove dashes and change extension to .png
        base = os.path.basename(jpg_file)
        num = ''.join(filter(str.isdigit, base))
        new_name = f"{prefix.rstrip('-')}{num}.png"
        new_path = os.path.join(folder_path, new_name)
        # Convert to PNG if not already
        try:
            with Image.open(jpg_file) as im:
                im.save(new_path)
            print(f"Converted {base} -> {new_name}")
            os.remove(jpg_file)
        except Exception as e:
            print(f"Error converting {base}: {e}")

def main():
    for folder, prefix in categories:
        convert_and_rename(folder, prefix)
    print("All images converted and renamed to .png!")

if __name__ == "__main__":
    main()
# Moved from project root to scripts/ as part of cleanup.
