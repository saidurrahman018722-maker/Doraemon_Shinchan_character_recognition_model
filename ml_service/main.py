import os
import io
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Doraemon & Shin-chan Character Recognition ML Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLASS_NAMES = [
    "bo_chan",
    "doraemon",
    "dorami",
    "himawari_nohara",
    "hiroshi_nohara",
    "masao_sato",
    "misae_nohara",
    "nene_sakurada",
    "nobi_nobita",
    "shiro_dog",
    "shizuka_minamoto",
    "suneo_honekawa",
    "takeshi_goda_gian",
    "toru_kazama"
]

CHARACTER_METADATA = {
    "doraemon": {"displayName": "Doraemon", "series": "Doraemon", "role": "Cat Robot from 22nd Century"},
    "nobi_nobita": {"displayName": "Nobita Nobi", "series": "Doraemon", "role": "Main Protagonist"},
    "shizuka_minamoto": {"displayName": "Shizuka Minamoto", "series": "Doraemon", "role": "Nobita's Best Friend & Future Wife"},
    "takeshi_goda_gian": {"displayName": "Takeshi 'Gian' Goda", "series": "Doraemon", "role": "Neighborhood Bully & Singer"},
    "suneo_honekawa": {"displayName": "Suneo Honekawa", "series": "Doraemon", "role": "Rich & Wealthy Friend"},
    "dorami": {"displayName": "Dorami", "series": "Doraemon", "role": "Doraemon's Younger Sister"},
    "misae_nohara": {"displayName": "Misae Nohara", "series": "Shin-chan", "role": "Shin-chan's Mother"},
    "hiroshi_nohara": {"displayName": "Hiroshi Nohara", "series": "Shin-chan", "role": "Shin-chan's Father"},
    "himawari_nohara": {"displayName": "Himawari Nohara", "series": "Shin-chan", "role": "Shin-chan's Baby Sister"},
    "shiro_dog": {"displayName": "Shiro", "series": "Shin-chan", "role": "Nohara Family Pet Dog"},
    "toru_kazama": {"displayName": "Toru Kazama", "series": "Shin-chan", "role": "Polite & Smart Kindergarten Friend"},
    "nene_sakurada": {"displayName": "Nene Sakurada", "series": "Shin-chan", "role": "Fiery Kindergarten Friend"},
    "masao_sato": {"displayName": "Masao Sato", "series": "Shin-chan", "role": "Timid & Sensitive Kindergarten Friend"},
    "bo_chan": {"displayName": "Bo-chan", "series": "Shin-chan", "role": "Quiet & Calm Kindergarten Friend"}
}

device = torch.device("cpu")
model = models.convnext_tiny(weights=None)
num_ftrs = model.classifier[2].in_features
model.classifier[2] = nn.Linear(num_ftrs, len(CLASS_NAMES))

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'doraemon_shinchan_model.pth')
if os.path.exists(MODEL_PATH):
    try:
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        model.float() # Ensure model is in FP32 regardless of saved checkpoint dtype
        print(f"Successfully loaded model from {MODEL_PATH}")
    except Exception as e:
        print(f"Warning: Failed to load model weights: {e}")
else:
    print(f"Warning: Model file not found at {MODEL_PATH}.")

model.to(device)
model.eval()

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

@app.get("/")
async def root():
    return {"message": "Doraemon & Shin-chan Character Recognition ML API is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": os.path.exists(MODEL_PATH)}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image.")

    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        input_tensor = transform(image)
        input_batch = input_tensor.unsqueeze(0).to(device)
        
        with torch.no_grad():
            output = model(input_batch)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            confidence, predicted_idx = torch.max(probabilities, 0)
            
        class_key = CLASS_NAMES[predicted_idx.item()]
        metadata = CHARACTER_METADATA.get(class_key, {"displayName": class_key, "series": "Unknown", "role": "Character"})
        
        top_3_values, top_3_indices = torch.topk(probabilities, k=min(3, len(CLASS_NAMES)))
        top_predictions = [
            {
                "class_name": CLASS_NAMES[idx.item()],
                "display_name": CHARACTER_METADATA.get(CLASS_NAMES[idx.item()], {}).get("displayName", CLASS_NAMES[idx.item()]),
                "confidence": round(val.item() * 100, 2)
            }
            for val, idx in zip(top_3_values, top_3_indices)
        ]
        
        return JSONResponse(content={
            "predicted_class": class_key,
            "display_name": metadata["displayName"],
            "series": metadata["series"],
            "role": metadata["role"],
            "confidence": round(confidence.item() * 100, 2),
            "top_predictions": top_predictions
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
