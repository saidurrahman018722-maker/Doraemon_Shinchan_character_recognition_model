import torch
import torchvision.transforms as transforms
import torch.nn as nn
from tqdm import tqdm
import torch.optim as optim
import torchvision.models as models
from torchvision import datasets
from torch.utils.data import DataLoader, WeightedRandomSampler
import numpy as np
from pathlib import Path
import multiprocessing
import warnings
import shutil

# Suppress PIL palette transparency warnings
warnings.filterwarnings("ignore", "(?s).*Palette images with Transparency expressed in bytes should be converted to RGBA images.*", category=UserWarning)

mean = (0.485, 0.456, 0.406)
std = (0.229, 0.224, 0.225)

train_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.RandomCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.TrivialAugmentWide(),
    transforms.ToTensor(),
    transforms.Normalize(mean=mean, std=std),
    transforms.RandomErasing(p=0.1)
])

val_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=mean, std=std)
])

SCRIPT_DIR = Path(__file__).resolve().parent
TRAIN_DIR = SCRIPT_DIR / "doraemon_shinchan_dataset" / "train"
VAL_DIR = SCRIPT_DIR / "doraemon_shinchan_dataset" / "val"
MODEL_SAVE_PATH = SCRIPT_DIR / "doraemon_shinchan_model.pth"
ML_SERVICE_MODEL_PATH = SCRIPT_DIR.parent.parent / "ml_service" / "doraemon_shinchan_model.pth"

best_val_acc = 0.0

def train_and_validate(epochs, current_optimizer, current_scheduler, phase_name, model, loss_fn, train_dataloader, test_dataloader, device):
    global best_val_acc
    for i in range(epochs):
        model.train()
        train_loss, train_acc = 0.0, 0.0
        loop = tqdm(train_dataloader, desc=f"[{phase_name}] Epoch {i+1}/{epochs} [Train]")
        for images, targets in loop:
            images, targets = images.to(device), targets.to(device)
            current_optimizer.zero_grad()
            y_logits = model(images)
            loss = loss_fn(y_logits, targets)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            current_optimizer.step()
            if current_scheduler:
                current_scheduler.step()
            train_loss += loss.item()
            y_pred = torch.argmax(y_logits, dim=1)
            train_acc += (y_pred == targets).float().mean().item()
            loop.set_postfix(loss=loss.item())

        train_loss /= len(train_dataloader)
        train_acc /= len(train_dataloader)

        model.eval()
        with torch.inference_mode():
            test_loss, test_acc = 0.0, 0.0
            for images, targets in tqdm(test_dataloader, desc=f"[{phase_name}] Epoch {i+1}/{epochs} [Val]"):
                images, targets = images.to(device), targets.to(device)
                y_test_logits = model(images)
                loss = loss_fn(y_test_logits, targets)
                test_loss += loss.item()
                y_test_pred = torch.argmax(y_test_logits, dim=1)
                test_acc += (y_test_pred == targets).float().mean().item()

        test_loss /= len(test_dataloader)
        test_acc /= len(test_dataloader)

        print(f"\n[{phase_name}] Epoch {i+1:02d} Summary:")
        print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc*100:.2f}%")
        print(f"Val Loss:   {test_loss:.4f} | Val Acc:   {test_acc*100:.2f}%")

        if test_acc >= best_val_acc:
            best_val_acc = test_acc
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            print(f"--> Saved new best model to {MODEL_SAVE_PATH.name} ({best_val_acc*100:.2f}% accuracy)")
            # Copy to ml_service folder if it exists
            ML_SERVICE_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(MODEL_SAVE_PATH, ML_SERVICE_MODEL_PATH)

if __name__ == '__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    train_dataset = datasets.ImageFolder(root=str(TRAIN_DIR), transform=train_transform, allow_empty=True)
    test_dataset = datasets.ImageFolder(root=str(VAL_DIR), transform=val_transform, allow_empty=True)

    num_workers = min(multiprocessing.cpu_count(), 4)
    classes = train_dataset.classes
    print(f"Found {len(classes)} classes: {classes}")

    # Compute sample weights for class balancing
    class_counts = [0] * len(classes)
    for _, idx in train_dataset.samples:
        class_counts[idx] += 1

    class_weights = [1.0 / count if count > 0 else 0 for count in class_counts]
    sample_weights = [class_weights[idx] for _, idx in train_dataset.samples]

    sampler = WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True
    )

    train_dataloader = DataLoader(train_dataset, batch_size=32, num_workers=num_workers, sampler=sampler)
    test_dataloader = DataLoader(test_dataset, batch_size=32, num_workers=num_workers, shuffle=False)

    # Initialize ConvNeXt-Tiny backbone pretrained on ImageNet
    model = models.convnext_tiny(weights=models.ConvNeXt_Tiny_Weights.DEFAULT)

    # Phase 1: Freeze backbone, train linear head
    for param in model.parameters():
        param.requires_grad = False

    num_features = model.classifier[2].in_features
    model.classifier[2] = nn.Linear(num_features, len(classes))
    model.to(device)

    loss_fn = nn.CrossEntropyLoss(label_smoothing=0.1)

    print("\n--- Phase 1: Training classifier head ---")
    phase1_epochs = 1
    optimizer_phase1 = optim.Adam(model.classifier[2].parameters(), lr=1e-3)
    train_and_validate(phase1_epochs, optimizer_phase1, None, "Phase 1", model, loss_fn, train_dataloader, test_dataloader, device)

    print("\n--- Phase 2: Unfreezing backbone & Fine-tuning ---")
    # Unfreeze all layers
    for param in model.parameters():
        param.requires_grad = True
        
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=4, gamma=0.1)
    
    train_and_validate(3, optimizer, scheduler, "Phase 2", model, loss_fn, train_dataloader, test_dataloader, device)

    print(f"\nTraining pipeline completed successfully! Best Accuracy: {best_val_acc*100:.2f}%")
