import os
import shutil

# Map of category to (static subfolder, base image name, count)
category_map = {
    'bus':    ('bus',    'bus1.jpg',    10),
    'train':  ('train',  'train1.jpg',  10),
    'cab':    ('cab',    'cab1.jpg',   7),
    'hotel':  ('hotels', 'hotel1.jpg', 10),
    'flight': ('air',    'air1.jpg',   10),
}

static_dir = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'images')

def copy_images():
    for cat, (folder, base_img, count) in category_map.items():
        folder_path = os.path.join(static_dir, folder)
        base_img_path = os.path.join(folder_path, base_img)
        if not os.path.exists(base_img_path):
            print(f"Base image missing: {base_img_path}")
            continue
        for i in range(1, count+1):
            target_img = f"{cat}{i}.jpg" if cat != 'hotel' else f"hotel{i}.jpg"
            target_path = os.path.join(folder_path, target_img)
            if not os.path.exists(target_path):
                shutil.copy(base_img_path, target_path)
                print(f"Copied {base_img} to {target_img}")
            else:
                print(f"Exists: {target_img}")

if __name__ == "__main__":
    copy_images()
# Moved from project root to scripts/ as part of cleanup.
