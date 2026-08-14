import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent / "doraemon_shinchan_dataset"
TRAIN_DIR = BASE_DIR / "train"
VAL_DIR = BASE_DIR / "val"

def balance_train_val():
    train_classes = [d for d in TRAIN_DIR.iterdir() if d.is_dir()]
    
    for char_dir in train_classes:
        char_name = char_dir.name
        val_char_dir = VAL_DIR / char_name
        val_char_dir.mkdir(parents=True, exist_ok=True)
        
        train_files = sorted([f for f in char_dir.glob("*.*") if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']])
        val_files = sorted([f for f in val_char_dir.glob("*.*") if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']])
        
        if len(val_files) == 0 and len(train_files) > 1:
            # Move 20% of train files to val
            move_count = max(1, min(10, len(train_files) // 5))
            for _ in range(move_count):
                file_to_move = train_files.pop()
                dest = val_char_dir / f"val_{file_to_move.name}"
                shutil.move(str(file_to_move), str(dest))
                
        t_after = len(list(char_dir.glob("*.*")))
        v_after = len(list(val_char_dir.glob("*.*")))
        print(f"[{char_name}] Balanced -> Train: {t_after}, Val: {v_after}")

if __name__ == "__main__":
    balance_train_val()
