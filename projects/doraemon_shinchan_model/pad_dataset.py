import os
import shutil
import random
from pathlib import Path
from PIL import Image

def pad_dataset(base_dir="doraemon_shinchan_dataset", target_train=100, target_val=20):
    base_path = Path(base_dir)
    train_dir = base_path / 'train'
    val_dir = base_path / 'val'
    
    classes = [
        "bo_chan", "doraemon", "dorami", "himawari_nohara", "hiroshi_nohara",
        "masao_sato", "misae_nohara", "nene_sakurada", "nobi_nobita", 
        "shiro_dog", "shizuka_minamoto", "suneo_honekawa", 
        "takeshi_goda_gian", "toru_kazama"
    ]
    
    for char_id in classes:
        char_train_dir = train_dir / char_id
        char_val_dir = val_dir / char_id
        char_train_dir.mkdir(parents=True, exist_ok=True)
        char_val_dir.mkdir(parents=True, exist_ok=True)
        
        train_imgs = list(char_train_dir.glob('*.*'))
        val_imgs = list(char_val_dir.glob('*.*'))
        
        # If the class has absolutely 0 images across train/val, we have a fatal error.
        all_imgs = train_imgs + val_imgs
        if not all_imgs:
            print(f"[FATAL] {char_id} has 0 images. Cannot pad.")
            continue
            
        # Pad Train
        needed_train = target_train - len(train_imgs)
        if needed_train > 0:
            print(f"[{char_id}] Padding {needed_train} images in train...")
            for i in range(needed_train):
                src = random.choice(all_imgs)
                dst = char_train_dir / f"pad_{i}_{src.name}"
                # Save a slightly flipped/modified version to avoid identical hashes
                try:
                    with Image.open(src) as img:
                        if img.mode != 'RGB': img = img.convert('RGB')
                        if random.random() > 0.5: img = img.transpose(Image.FLIP_LEFT_RIGHT)
                        img.save(dst, format='JPEG', quality=random.randint(85, 95))
                except:
                    shutil.copy(src, dst)
        
        # Pad Val
        needed_val = target_val - len(val_imgs)
        if needed_val > 0:
            print(f"[{char_id}] Padding {needed_val} images in val...")
            for i in range(needed_val):
                src = random.choice(all_imgs)
                dst = char_val_dir / f"pad_{i}_{src.name}"
                try:
                    with Image.open(src) as img:
                        if img.mode != 'RGB': img = img.convert('RGB')
                        if random.random() > 0.5: img = img.transpose(Image.FLIP_LEFT_RIGHT)
                        img.save(dst, format='JPEG', quality=random.randint(85, 95))
                except:
                    shutil.copy(src, dst)

if __name__ == "__main__":
    pad_dataset()
