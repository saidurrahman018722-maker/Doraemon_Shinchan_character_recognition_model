import sys
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TRAIN_DIR = SCRIPT_DIR / "doraemon_shinchan_dataset" / "train"
MODEL_PATH = SCRIPT_DIR / "doraemon_shinchan_model.pth"

# Load class names dynamically from folder structure
if TRAIN_DIR.exists():
    CLASS_NAMES = sorted([d.name for d in TRAIN_DIR.iterdir() if d.is_dir()])
else:
    CLASS_NAMES = [
        "bo_chan", "doraemon", "dorami", "himawari_nohara", "hiroshi_nohara",
        "masao_sato", "misae_nohara", "nene_sakurada", "nobi_nobita",
        "shiro_dog", "shinnosuke_nohara", "shizuka_minamoto",
        "suneo_honekawa", "takeshi_goda_gian", "toru_kazama"
    ]

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def load_model(num_classes):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.convnext_tiny(weights=None)
    num_ftrs = model.classifier[2].in_features
    model.classifier[2] = nn.Linear(num_ftrs, num_classes)
    
    if MODEL_PATH.exists():
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        print(f"Loaded weights from {MODEL_PATH}")
    else:
        print(f"Error: Model weight file not found at {MODEL_PATH}")
        sys.exit(1)
        
    model.to(device)
    model.eval()
    return model, device

def predict_image(image_path, model, device):
    img = Image.open(image_path).convert('RGB')
    tensor = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.nn.functional.softmax(outputs[0], dim=0)
        conf, pred_idx = torch.max(probs, dim=0)
    return CLASS_NAMES[pred_idx.item()], conf.item()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python model_testing.py <path_to_image>")
        sys.exit(0)
    
    image_path = sys.argv[1]
    model, device = load_model(len(CLASS_NAMES))
    pred_label, confidence = predict_image(image_path, model, device)
    print(f"\nPrediction for {image_path}:")
    print(f"Class: {pred_label} (Confidence: {confidence*100:.2f}%)")
