import torch
import torchvision.transforms as transforms
from PIL import Image
from torchvision import models
from torchvision.models import ResNet18_Weights

# Load model once globally
model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
model.eval()
labels = ResNet18_Weights.DEFAULT.meta["categories"]

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),  # Converts to [0, 1]
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])


def classify_image(img: Image.Image) -> dict:
    tensor = transform(img).unsqueeze(0)  # Add batch dimension

    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.nn.functional.softmax(outputs[0], dim=0)
        confidence, class_idx = torch.max(probs, dim=0)

    return {
        "top_class": labels[class_idx],
        "confidence": confidence.item()
    }
