import cv2
import numpy as np
import torch
import onnxruntime as ort

# 載入 YOLOv5 模型
yolo_model = torch.hub.load('ultralytics/yolov5', 'custom', path='models/best.pt', force_reload=True)

# 載入 ONNX OCR 模型
ocr_session = ort.InferenceSession('models/ocr_model.onnx')

def preprocess_image(image):
    # 根據 OCR 模型需求進行預處理
    image = cv2.resize(image, (100, 32))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = image.astype(np.float32) / 255.0
    image = np.expand_dims(image, axis=0)  # Add channel dimension
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image

def postprocess_output(output):
    # 將模型輸出轉換為文字（需根據模型設計調整）
    # 此處為示意，實際需根據模型輸出格式解析
    predicted_text = "示意文字"
    return predicted_text

def detect_and_recognize(image_path):
    image = cv2.imread(image_path)
    results = yolo_model(image)
    crops = results.crop(save=False)

    recognized_texts = []

    for crop in crops:
        cropped_img = crop['im']
        input_tensor = preprocess_image(cropped_img)
        ort_inputs = {ocr_session.get_inputs()[0].name: input_tensor}
        ort_outs = ocr_session.run(None, ort_inputs)
        text = postprocess_output(ort_outs)
        recognized_texts.append(text)

    return recognized_texts
