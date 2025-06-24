import os
from shutil import move
import numpy as np
from ultralytics import YOLO
import cv2


class UltralyticsModel():
    def __init__(self, model_type, classes, checkpoint, image_size=640):    # TODO change default size
        super().__init__()

        self.model_type = model_type
        self.classes = classes
        self.checkpoint = checkpoint
        self.image_size = image_size

        if model_type == 'YOLO':
            self.model = YOLO(checkpoint)
        else:
            raise NotImplementedError
    
    @staticmethod
    def train(dataset_path, output_path, model='yolov11s.pt', image_size=224, device='cuda', epochs=50, batch=16):
        model = YOLO(model)

        result = model.train(
            data=dataset_path,
            # save_dir=output_path, # fail
            epochs=epochs,
            imgsz=image_size,
            batch=batch,
            device=device,
        )

        # fix save dir
        move(os.path.join(os.getcwd(), result.save_dir), output_path)

        return result
        
    def run(self, image):
        multi = image.ndim > 3

        # run model
        results = self.model.predict(source=image, imgsz=self.image_size, save=False, stream=False, verbose=False)

        if not multi:
            return results[0]
        
        # TODO standard API for results
            
        return results

