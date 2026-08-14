import os
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent / "doraemon_shinchan_dataset"

def verify_and_clean_images(directory):
    removed_count = 0
    valid_count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
                continue
            try:
                with Image.open(file_path) as img:
                    img.verify()  # Verify that it is a valid image
                # Re-open for actual loading test
                with Image.open(file_path) as img:
                    img.convert('RGB')
                valid_count += 1
            except Exception as e:
                print(f"Removing corrupt image: {file_path} ({e})")
                file_path.unlink(missing_ok=True)
                removed_count += 1
    return valid_count, removed_count

if __name__ == "__main__":
    print(f"Verifying images in {BASE_DIR}...")
    valid, removed = verify_and_clean_images(BASE_DIR)
    print(f"Verification completed. Valid images: {valid}, Corrupt/Removed images: {removed}")
