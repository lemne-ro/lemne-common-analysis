import numpy as np
from ultralytics import YOLO
import cv2


class UltralyticsModel():
    def __init__(self, model_type, classes, checkpoint, image_size=640):
        super().__init__()

        self.model_type = model_type
        self.classes = classes
        self.checkpoint = checkpoint
        self.image_size = image_size

        if model_type == 'YOLO':
            self.model = YOLO(checkpoint)
        else:
            raise NotImplementedError
        
    def run(self, image):
        multi = image.ndim > 3

        # run model
        results = self.model.predict(source=image, imgsz=self.image_size, save=False, stream=False, verbose=False)

        if not multi:
            return results[0]
            
        return results

