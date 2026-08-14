import os
import shutil
import random
from pathlib import Path

def rebalance_dataset(base_dir, val_split=0.2):
    base_path = Path(base_dir)
    train_dir = base_path / 'train'
    val_dir = base_path / 'val'
    
    val_dir.mkdir(parents=True, exist_ok=True)
    
    for char_dir in train_dir.iterdir():
        if not char_dir.is_dir(): continue
        
        char_name = char_dir.name
        val_char_dir = val_dir / char_name
        val_char_dir.mkdir(exist_ok=True)
        
        images = list(char_dir.glob('*.jpg')) + list(char_dir.glob('*.png')) + list(char_dir.glob('*.jpeg'))
        
        # If there are already images in val, count them
        val_images = list(val_char_dir.glob('*.jpg')) + list(val_char_dir.glob('*.png')) + list(val_char_dir.glob('*.jpeg'))
        
        total_images = len(images) + len(val_images)
        if total_images == 0:
            print(f"{char_name}: No images found.")
            continue
            
        target_val = max(1, int(total_images * val_split)) # At least 1 val image if possible
        
        needed_in_val = target_val - len(val_images)
        
        if needed_in_val > 0 and len(images) > 1:
            # Move needed_in_val images from train to val
            to_move = random.sample(images, min(needed_in_val, len(images) - 1)) # Keep at least 1 in train
            for img_path in to_move:
                shutil.move(str(img_path), str(val_char_dir / img_path.name))
            print(f"{char_name}: Moved {len(to_move)} images to val.")
        else:
            print(f"{char_name}: No rebalance needed. (Train: {len(images)}, Val: {len(val_images)})")

if __name__ == "__main__":
    rebalance_dataset("doraemon_shinchan_dataset")
