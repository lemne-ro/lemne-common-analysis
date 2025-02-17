import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms


class TorchModel():
    def __init__(self, model_type, classes, checkpoint=None, image_size=224):
        super().__init__()

        self.model_type = model_type
        self.classes = classes
        self.checkpoint = checkpoint

        self.model = self.get_model(model_type, len(classes), checkpoint)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize((image_size, image_size)),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
    
    @staticmethod
    def get_model(model_type, num_classes, checkpoint=None):
        if model_type == 'resnet18':
            model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
            model.fc = nn.Linear(model.fc.in_features, num_classes)
        elif model_type == 'mobilenet_v3_small':
            model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
            model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, num_classes)
        elif model_type == 'efficientnet_b0':
            model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
            model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, num_classes)
            model_type = model._get_name()
            model._get_name = lambda: f'{model_type}_B0'
        else:
            raise NotImplementedError
        
        if checkpoint is not None:
            model.load_state_dict(torch.load(checkpoint))

        return model
    
    def run(self, image):
        image = self.transform(image)
        image = image[None]

        output = self.model(image)
        scores = F.softmax(output, dim=1)
        # scores, preds = torch.max(scores, 1)

        scores = scores[0].detach().cpu().numpy()

        result = {key: scores[i] for i, key in enumerate(self.classes)}

        return result


